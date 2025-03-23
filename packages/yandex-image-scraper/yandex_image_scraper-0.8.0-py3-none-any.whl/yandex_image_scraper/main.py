#!/usr/bin/env python3
"""
Yandex Image Scraper using Camoufox - A tool to scrape and download images from Yandex search results
"""

import asyncio
import os
import re
import html
import urllib.parse
import random
from pathlib import Path
from typing import List

import aiohttp
from camoufox.async_api import AsyncCamoufox

# List of common user agents for randomization
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

def extract_image_urls(html_content: str) -> List[str]:
    """
    Extract image URLs from Yandex search results HTML
    """
    # Find all img_url parameters
    pattern = r'img_url=(.*?)(?:&amp;|")'
    matches = re.findall(pattern, html_content)
    
    # URL decode the matches
    decoded_urls = []
    for match in matches:
        try:
            # First unescape HTML entities like &amp;
            unescaped = html.unescape(match)
            # Then decode URL encoding
            decoded = urllib.parse.unquote(unescaped)
            # Clean up any remaining artifacts
            decoded = decoded.split('&')[0]
            decoded_urls.append(decoded)
        except Exception as e:
            print(f"Error decoding URL: {str(e)}")
    
    # Remove duplicates while preserving order
    unique_urls = []
    seen = set()
    for url in decoded_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
            
    return unique_urls

async def download_image(session: aiohttp.ClientSession, url: str, folder: Path, index: int) -> None:
    """Download a single image"""
    try:
        # Pick a random user agent
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        
        async with session.get(url, headers=headers, allow_redirects=True) as response:
            if response.status == 200:
                # Get file extension from content type
                content_type = response.headers.get('Content-Type', '')
                if 'image/jpeg' in content_type or 'image/jpg' in content_type:
                    ext = '.jpg'
                elif 'image/png' in content_type:
                    ext = '.png'
                elif 'image/gif' in content_type:
                    ext = '.gif'
                elif 'image/webp' in content_type:
                    ext = '.webp'
                else:
                    # Try to extract extension from URL
                    url_ext = re.search(r'\.([a-zA-Z0-9]+)(?:[\?#]|$)', url)
                    if url_ext and url_ext.group(1).lower() in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                        ext = f".{url_ext.group(1).lower()}"
                    else:
                        ext = '.jpg'  # Default to jpg
                
                file_path = folder / f"image_{index:04d}{ext}"
                with open(file_path, 'wb') as f:
                    f.write(await response.read())
                print(f"Downloaded: {file_path.name}")
            else:
                print(f"Failed to download image {index}: HTTP {response.status}")
    except Exception as e:
        print(f"Error downloading image {index}: {str(e)}")

async def download_images(image_urls: List[str], folder_path: Path) -> None:
    """
    Download images concurrently
    """
    # Create folder if it doesn't exist
    folder_path.mkdir(exist_ok=True, parents=True)
    
    # Create a session for downloading
    timeout = aiohttp.ClientTimeout(total=60)
    connector = aiohttp.TCPConnector(limit=50, force_close=True, enable_cleanup_closed=True)
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        # Process images in batches of 50
        for i in range(0, len(image_urls), 50):
            batch = image_urls[i:i+50]
            tasks = [download_image(session, url, folder_path, i+idx) for idx, url in enumerate(batch)]
            await asyncio.gather(*tasks)
            
            # Short delay between batches with randomization (reduced delay)
            if i + 50 < len(image_urls):
                wait_time = 0.5 + random.uniform(0.2, 0.5)
                await asyncio.sleep(wait_time)

async def save_urls_to_file(urls: List[str], filename: str) -> None:
    """Save image URLs to a text file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(f"{url}\n")
    print(f"Saved {len(urls)} URLs to {filename}")

async def scrape_yandex_images(
    search_query: str,
    num_images: int,
    content_type: str = None,
    image_size: str = None,
    orientation: str = None,
    download: bool = True,
    save_urls: bool = True
) -> List[str]:
    """
    Scrape Yandex images using Camoufox
    """
    # Configure Camoufox with minimal settings
    browser_config = {
        "headless": False,
    }
    
    # Properly encode the query
    encoded_query = urllib.parse.quote(search_query.encode('utf-8'), safe='')
    url = f"https://yandex.com/images/search?lr=10511&source=related-duck&text={encoded_query}"
    
    # Add filters if specified
    if content_type:
        url += f"&type={content_type}"
    
    if image_size:
        url += f"&isize={image_size}"
    
    if orientation:
        url += f"&iorient={orientation}"
    
    image_urls = []
    
    async with AsyncCamoufox(**browser_config) as browser:
        page = await browser.new_page()
        
        print(f"Navigating to: {url}")
        
        # Navigate to the search page and wait for results with redirect handling
        await page.goto(url, wait_until="domcontentloaded")
        
        # Check if we need to solve a captcha
        if await page.query_selector("form.captcha-wrapper") is not None:
            print("CAPTCHA detected! Please solve it manually...")
            # Wait for user to solve captcha
            await page.wait_for_selector(".serp-item", timeout=300000)  # 5 minute timeout
        
        # Wait for search results to load
        await page.wait_for_load_state("networkidle")
        
        # Scroll and collect images until we have enough
        scroll_attempts = 0
        max_scroll_attempts = 50  # Safety limit
        button_not_found_count = 0
        max_button_not_found = 3  # Exit after failing to find button 3 times
        
        while len(image_urls) < num_images and scroll_attempts < max_scroll_attempts:
            # Get the page content and extract image URLs
            html_content = await page.content()
            page_urls = extract_image_urls(html_content)
            
            # Add new URLs to our collection
            initial_count = len(image_urls)
            image_urls.extend([url for url in page_urls if url not in image_urls])
            new_count = len(image_urls)
            
            print(f"Found {new_count - initial_count} new images. Total: {new_count}")
            
            # If we've found enough images, break
            if len(image_urls) >= num_images:
                break
                
            # If we didn't get any new images after 3 consecutive scrolls, try clicking "Show more" button
            if new_count == initial_count:
                scroll_attempts += 1
                if scroll_attempts >= 3:
                    print("No new images found after multiple scrolls. Looking for 'Show more' button...")
                    
                    # Try to find and click the "Show more" button
                    show_more_button = await page.query_selector('.Button_width_max')
                    
                    if show_more_button:
                        print("Found 'Show more' button. Clicking...")
                        await show_more_button.click()
                        await page.wait_for_load_state("networkidle")
                        await asyncio.sleep(2)  # Wait for new content to load
                        scroll_attempts = 0  # Reset scroll attempts
                        button_not_found_count = 0  # Reset button not found counter
                    else:
                        print("'Show more' button not found.")
                        button_not_found_count += 1
                        if button_not_found_count >= max_button_not_found:
                            print(f"Failed to find 'Show more' button {max_button_not_found} times. Stopping.")
                            break
            else:
                scroll_attempts = 0  # Reset counter if we found new images
            
            # Scroll down to load more images
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(2 + random.uniform(0.5, 1.5))  # Wait for new images to load
    
    # Limit to requested number of images
    image_urls = image_urls[:num_images]
    
    # Display the found URLs
    print(f"\nFound {len(image_urls)} images in total:")
    for i, url in enumerate(image_urls[:5], 1):
        print(f"{i}. {url}")
    
    if len(image_urls) > 5:
        print(f"... and {len(image_urls) - 5} more")
    
    # Save URLs to file if requested
    if save_urls and image_urls:
        folder_name = re.sub(r'[^\w\-_]', '_', search_query)
        url_file = Path(os.getcwd()) / f"{folder_name}_urls.txt"
        await save_urls_to_file(image_urls, str(url_file))
    
    # Download images if requested
    if download and image_urls:
        # Create a folder based on the search query
        folder_name = re.sub(r'[^\w\-_]', '_', search_query)
        folder_path = Path(os.getcwd()) / folder_name
        
        print(f"\nDownloading images to: {folder_path}")
        await download_images(image_urls, folder_path)
        print(f"\nDownloaded {len(image_urls)} images to {folder_path}")
    
    return image_urls

async def async_main():
    """Async main function - handles the core application logic"""
    # Get user input
    search_query = input("Enter search query: ")
    num_images = int(input("How many images to download? [20]: ") or "20")
    
    # Ask for content type
    content_types = ["photo", "clipart", "lineart", "face", "demotivator", "none"]
    print("Content type options: " + ", ".join(content_types))
    content_type = input("Content type filter [photo]: ") or "photo"
    content_type = None if content_type.lower() == "none" else content_type.lower()
    
    # Ask for image size
    sizes = ["large", "medium", "small", "none"]
    print("Image size options: " + ", ".join(sizes))
    image_size = input("Image size filter [large]: ") or "large"
    image_size = None if image_size.lower() == "none" else image_size.lower()
    
    # Ask for orientation
    orientations = ["horizontal", "vertical", "square", "none"]
    print("Orientation options: " + ", ".join(orientations))
    orientation = input("Image orientation filter [none]: ") or "none"
    orientation = None if orientation.lower() == "none" else orientation.lower()
    
    # Ask if user wants to download
    download_input = input("Download images? [Y/n]: ").lower()
    download = not (download_input == "n" or download_input == "no")
    
    # Ask if user wants to save URLs
    save_urls_input = input("Save URLs to file? [Y/n]: ").lower()
    save_urls = not (save_urls_input == "n" or save_urls_input == "no")
    
    # Run the scraper
    print(f"\nStarting Yandex image scraper using Camoufox for: {search_query}")
    
    await scrape_yandex_images(
        search_query,
        num_images,
        content_type,
        image_size,
        orientation,
        download,
        save_urls
    )

def main():
    """
    Main entry point - this is a synchronous function that runs the async main
    """
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    main()
