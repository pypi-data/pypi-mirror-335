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
import argparse
from pathlib import Path
from typing import List, Optional

import aiohttp
from camoufox.async_api import AsyncCamoufox

# Import spoofing configuration
from yandex_image_scraper.spoofing import generate_spoofing_config
# Import tor handler
from yandex_image_scraper.tor_handler import is_tor_running, get_tor_browser_config, check_tor_connection

# List of common user agents for randomization
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

def extract_image_urls(html_content: str) -> List[str]:
    """
    Extract image URLs from Yandex search results HTML
    """
    # Find all img_url parameters
    pattern: str = r'img_url=(.*?)(?:&amp;|")'
    matches: List[str] = re.findall(pattern, html_content)
    
    # URL decode the matches
    decoded_urls: List[str] = []
    for match in matches:
        try:
            # First unescape HTML entities like &amp;
            unescaped: str = html.unescape(match)
            # Then decode URL encoding
            decoded: str = urllib.parse.unquote(unescaped)
            # Clean up any remaining artifacts
            decoded = decoded.split('&')[0]
            decoded_urls.append(decoded)
        except Exception as e:
            print(f"Error decoding URL: {str(e)}")
    
    # Remove duplicates while preserving order
    unique_urls: List[str] = []
    seen: set = set()
    for url in decoded_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
            
    return unique_urls

async def download_image(session: aiohttp.ClientSession, url: str, folder: Path, index: int) -> None:
    """Download a single image"""
    try:
        # Pick a random user agent
        headers: dict[str, str] = {"User-Agent": random.choice(USER_AGENTS)}
        
        async with session.get(url, headers=headers, allow_redirects=True) as response:
            if response.status == 200:
                # Get file extension from content type
                content_type: str = response.headers.get('Content-Type', '')
                if 'image/jpeg' in content_type or 'image/jpg' in content_type:
                    ext: str = '.jpg'
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
                
                file_path: Path = folder / f"image_{index:04d}{ext}"
                with open(file_path, 'wb') as f:
                    f.write(await response.read())
                print(f"Downloaded: {file_path.name}")
            else:
                print(f"Failed to download image {index}: HTTP {response.status}")
    except Exception as e:
        print(f"Error downloading image {index}: {str(e)}")

async def download_images(image_urls: List[str], folder_path: Path) -> None:
    """
    Download images concurrently in smaller batches
    """
    # Create folder if it doesn't exist
    folder_path.mkdir(exist_ok=True, parents=True)
    
    # Create a session for downloading
    timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=60)
    connector: aiohttp.TCPConnector = aiohttp.TCPConnector(limit=50, force_close=True, enable_cleanup_closed=True)
    
    # Configure session with Tor proxy if requested
    session_kwargs = {"timeout": timeout, "connector": connector}
    
    async with aiohttp.ClientSession(**session_kwargs) as session:
        # Create batches of 25 images max
        batch_size: int = 25
        batches: List[List[str]] = [image_urls[i:i+batch_size] for i in range(0, len(image_urls), batch_size)]
        
        print(f"Processing {len(image_urls)} images in {len(batches)} batches of max {batch_size} images each")
        
        # Create a task for each batch and run them all concurrently
        batch_tasks: List[asyncio.Task] = []
        for batch_idx, batch in enumerate(batches):
            batch_tasks.append(
                asyncio.create_task(
                    process_batch(session, batch, folder_path, batch_idx * batch_size)
                )
            )
        
        # Wait for all batches to complete
        await asyncio.gather(*batch_tasks)

async def process_batch(session: aiohttp.ClientSession, batch: List[str], folder_path: Path, start_idx: int) -> None:
    """Process a batch of image downloads"""
    tasks: List[asyncio.Task] = [download_image(session, url, folder_path, start_idx + idx) for idx, url in enumerate(batch)]
    await asyncio.gather(*tasks)

async def save_urls_to_file(urls: List[str], filename: str) -> None:
    """Save image URLs to a text file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(f"{url}\n")
    print(f"Saved {len(urls)} URLs to {filename}")

async def scrape_yandex_images(
    search_query: str,
    num_images: int,
    content_type: Optional[str] = None,
    image_size: Optional[str] = None,
    orientation: Optional[str] = None,
    download: bool = True,
    save_urls: bool = False,  # Changed default to False
    headless: bool = True,     # Changed default to True
    use_tor: bool = False      # New parameter for Tor routing
) -> List[str]:
    """
    Scrape Yandex images using Camoufox
    """
    # Generate spoofing configuration
    spoofing_config = generate_spoofing_config()
    
    # Configure Camoufox with basic settings
    browser_config: dict = {
        "headless": headless,
    }
    
    # Add Tor proxy configuration if required
    if use_tor:
        if not is_tor_running():
            print("Error: Tor proxy is not running. Please start Tor and try again.")
            return []
            
        print("Using Tor for anonymous browsing (SOCKS5 proxy)")
        tor_config = get_tor_browser_config()
        browser_config.update(tor_config)
        
        # Test Tor connection
        print("Testing Tor connection...")
        is_tor, ip = await check_tor_connection()
        if is_tor:
            print(f"Successfully connected to Tor network. IP: {ip}")
        else:
            print("Warning: Connected to proxy but Tor verification failed. Proceeding anyway...")
    
    print("Using browser fingerprint spoofing to avoid detection")
    
    # Properly encode the query
    encoded_query: str = urllib.parse.quote(search_query.encode('utf-8'), safe='')
    url: str = f"https://yandex.com/images/search?lr=10511&source=related-duck&text={encoded_query}"
    
    # Add filters if specified
    if content_type:
        url += f"&type={content_type}"
    
    if image_size:
        url += f"&isize={image_size}"
    
    if orientation:
        url += f"&iorient={orientation}"
    
    image_urls: List[str] = []
    
    async with AsyncCamoufox(**browser_config) as browser:
        # Create a new page with custom headers
        context = await browser.new_context(
            viewport={
                "width": spoofing_config['js_params']['screen']['width'],
                "height": spoofing_config['js_params']['screen']['height']
            },
            locale=f"{spoofing_config['locale']['language']}-{spoofing_config['locale']['region']}",
            timezone_id=spoofing_config['locale']['timezone'],
            user_agent=spoofing_config['headers']['User-Agent']
        )
        page = await context.new_page()
        
        # Set extra HTTP headers
        await page.set_extra_http_headers(spoofing_config['headers'])
            
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
        scroll_attempts: int = 0
        max_scroll_attempts: int = 50  # Safety limit
        button_not_found_count: int = 0
        max_button_not_found: int = 3  # Exit after failing to find button 3 times
        
        while len(image_urls) < num_images and scroll_attempts < max_scroll_attempts:
            # Get the page content and extract image URLs
            html_content: str = await page.content()
            page_urls: List[str] = extract_image_urls(html_content)
            
            # Add new URLs to our collection
            initial_count: int = len(image_urls)
            image_urls.extend([url for url in page_urls if url not in image_urls])
            new_count: int = len(image_urls)
            
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
        folder_name: str = re.sub(r'[^\w\-_]', '_', search_query)
        url_file: Path = Path(os.getcwd()) / f"{folder_name}_urls.txt"
        await save_urls_to_file(image_urls, str(url_file))
    
    # Download images if requested
    if download and image_urls:
        # Create a folder based on the search query
        folder_name: str = re.sub(r'[^\w\-_]', '_', search_query)
        folder_path: Path = Path(os.getcwd()) / folder_name
        
        print(f"\nDownloading images to: {folder_path}")
        await download_images(image_urls, folder_path)
        print(f"\nDownloaded {len(image_urls)} images to {folder_path}")
    
    return image_urls

async def async_main() -> None:
    """Async main function - handles the core application logic"""
    # Parse command line arguments first
    parser = argparse.ArgumentParser(description="Yandex Image Scraper with Camoufox")
    parser.add_argument("--tor", action="store_true", help="Route traffic through Tor (requires Tor to be running)")
    parser.add_argument("--query", type=str, help="Search query")
    parser.add_argument("--num-images", type=int, default=20, help="Number of images to download (default: 20)")
    parser.add_argument("--content-type", type=str, choices=["photo", "clipart", "lineart", "face", "demotivator", "none"], 
                       help="Content type filter")
    parser.add_argument("--image-size", type=str, choices=["large", "medium", "small", "none"], 
                       help="Image size filter")
    parser.add_argument("--orientation", type=str, choices=["horizontal", "vertical", "square", "none"], 
                       help="Image orientation filter")
    parser.add_argument("--no-download", action="store_true", help="Don't download images, just get URLs")
    parser.add_argument("--save-urls", action="store_true", help="Save URLs to a text file")
    parser.add_argument("--no-headless", action="store_true", help="Run browser in visible mode")
    
    args = parser.parse_args()
    use_tor = args.tor
    
    # Get search query from command line or prompt
    search_query: str = args.query if args.query else input("Enter search query: ")
    
    # Get number of images from command line or prompt
    num_images: int = args.num_images if args.num_images else int(input("How many images to download? [20]: ") or "20")
    
    # Handle content type
    if args.content_type:
        content_type = None if args.content_type.lower() == "none" else args.content_type.lower()
    else:
        content_types: List[str] = ["photo", "clipart", "lineart", "face", "demotivator", "none"]
        print("Content type options: " + ", ".join(content_types))
        content_type_input: str = input("Content type filter [photo]: ") or "photo"
        content_type = None if content_type_input.lower() == "none" else content_type_input.lower()
    
    # Handle image size
    if args.image_size:
        image_size = None if args.image_size.lower() == "none" else args.image_size.lower()
    else:
        sizes: List[str] = ["large", "medium", "small", "none"]
        print("Image size options: " + ", ".join(sizes))
        image_size_input: str = input("Image size filter [large]: ") or "large"
        image_size = None if image_size_input.lower() == "none" else image_size_input.lower()
    
    # Handle orientation
    if args.orientation:
        orientation = None if args.orientation.lower() == "none" else args.orientation.lower()
    else:
        orientations: List[str] = ["horizontal", "vertical", "square", "none"]
        print("Orientation options: " + ", ".join(orientations))
        orientation_input: str = input("Image orientation filter [none]: ") or "none"
        orientation = None if orientation_input.lower() == "none" else orientation_input.lower()
    
    # Handle download option
    if args.no_download:
        download = False
    else:
        download_input: str = input("Download images? [Y/n]: ").lower()
        download = not (download_input == "n" or download_input == "no")
    
    # Handle save URLs option
    if args.save_urls:
        save_urls = True
    else:
        save_urls_input: str = input("Save URLs to file? [Y/n]: ").lower()
        save_urls = not (save_urls_input == "n" or save_urls_input == "no")
    
    # Handle headless mode
    if args.no_headless:
        headless = False
    else:
        headless_input: str = input("Run in headless mode? [y/N]: ").lower()
        headless = headless_input == "y" or headless_input == "yes"
    
    # Run the scraper
    print(f"\nStarting Yandex image scraper using Camoufox for: {search_query}")
    if use_tor:
        print("Routing traffic through Tor SOCKS proxy")
    
    await scrape_yandex_images(
        search_query,
        num_images,
        content_type,
        image_size,
        orientation,
        download,
        save_urls,
        headless,
        use_tor
    )

def main() -> int:
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
