#!/usr/bin/env python3
"""
Yandex Image Scraper - A tool to scrape and download images from Yandex search results
"""

import asyncio
import os
import re
import html
import urllib.parse
from pathlib import Path
from typing import List

import aiohttp
import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

app = typer.Typer(help="Yandex Image Scraper CLI")


async def fetch_page_html(
    session: aiohttp.ClientSession, 
    query: str, 
    page: int = 1,
    content_type: str = None,
    image_size: str = None,
    orientation: str = None
) -> str:
    """
    Fetch HTML from Yandex image search for a given page
    """
    encoded_query = urllib.parse.quote(query)
    url = f"https://yandex.com/images/search?lr=10511&source=related-duck&text={encoded_query}"
    
    # Add filters if specified
    if content_type:
        url += f"&type={content_type}"
    
    if image_size:
        url += f"&isize={image_size}"
    
    if orientation:
        url += f"&iorient={orientation}"
        
    # Add pagination parameter if not the first page
    if page > 1:
        url += f"&p={page}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/100.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    
    typer.echo(f"Requesting URL: {url}")
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.text()
        else:
            typer.echo(f"Failed to fetch page {page}: HTTP {response.status}")
            return ""


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
            typer.echo(f"Error decoding URL: {str(e)}")
    
    # Remove duplicates while preserving order
    unique_urls = []
    seen = set()
    for url in decoded_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
            
    return unique_urls


async def download_image(session: aiohttp.ClientSession, url: str, folder: Path, index: int) -> None:
    """
    Download an image from a URL
    """
    try:
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                # Try to get file extension from URL or content-type
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
                typer.echo(f"Downloaded: {file_path.name}")
                return
            else:
                typer.echo(f"Failed to download image {index}: HTTP {response.status}")
    except Exception as e:
        typer.echo(f"Error downloading image {index}: {str(e)}")


async def download_images(image_urls: List[str], folder: Path) -> None:
    """
    Download images concurrently
    """
    # Create folder if it doesn't exist
    folder.mkdir(exist_ok=True, parents=True)
    
    # Create a client session
    async with aiohttp.ClientSession() as session:
        # Process images in batches of 10
        for i in range(0, len(image_urls), 10):
            batch = image_urls[i:i+10]
            tasks = [download_image(session, url, folder, i+idx) for idx, url in enumerate(batch)]
            await asyncio.gather(*tasks)
            
            # Short delay between batches
            if i + 10 < len(image_urls):
                await asyncio.sleep(1)


async def save_urls_to_file(urls: List[str], filename: str) -> None:
    """
    Save image URLs to a text file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(f"{url}\n")
    typer.echo(f"Saved {len(urls)} URLs to {filename}")


async def run_scraper(
    search_query: str, 
    num_images: int,
    content_type: str = None,
    image_size: str = None,
    orientation: str = None,
    download: bool = True, 
    save_urls: bool = True,
    max_pages: int = 20
) -> List[str]:
    """
    Run the scraper with given parameters
    """
    image_urls = []
    current_page = 1
    
    async with aiohttp.ClientSession() as session:
        # Continue scraping pages until we have enough images or reach max_pages
        while len(image_urls) < num_images and current_page <= max_pages:
            typer.echo(f"Scraping page {current_page}...")
            html_content = await fetch_page_html(
                session, 
                search_query, 
                current_page,
                content_type,
                image_size,
                orientation
            )
            
            if not html_content:
                typer.echo(f"No content found on page {current_page}. Stopping.")
                break
            
            page_urls = extract_image_urls(html_content)
            
            # If no new images found on this page, we've reached the end
            if not page_urls:
                typer.echo(f"No more images found after page {current_page}. Stopping.")
                break
                
            # Add new URLs to our collection
            initial_count = len(image_urls)
            image_urls.extend(page_urls)
            new_count = len(image_urls)
            
            typer.echo(f"Found {new_count - initial_count} new images on page {current_page}")
            
            # If we didn't get any new images (all were duplicates), we're probably at the end
            if new_count == initial_count:
                typer.echo("No new unique images found. Stopping.")
                break
                
            # Move to next page
            current_page += 1
            
            # Delay between pages to avoid rate limiting
            if len(image_urls) < num_images and current_page <= max_pages:
                await asyncio.sleep(2)
    
    # Limit to requested number of images
    image_urls = image_urls[:num_images]
    
    # Display the found URLs
    typer.echo(f"\nFound {len(image_urls)} images in total:")
    for i, url in enumerate(image_urls[:5], 1):
        typer.echo(f"{i}. {url}")
    
    if len(image_urls) > 5:
        typer.echo(f"... and {len(image_urls) - 5} more")
    
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
        
        typer.echo(f"\nDownloading images to: {folder_path}")
        await download_images(image_urls, folder_path)
        typer.echo(f"\nDownloaded {len(image_urls)} images to {folder_path}")
    
    return image_urls


@app.command()
def scrape() -> None:
    """
    Scrape images from Yandex based on a search query
    """
    # Get search query from user
    search_query = typer.prompt("Enter search query")
    
    # Get number of images to scrape
    num_images = typer.prompt(
        "How many images do you want to scrape?",
        type=int,
        default=20
    )
    
    # Content type filter
    content_type_completer = WordCompleter(['photo', 'clipart', 'lineart', 'face', 'demotivator', 'none'])
    content_type = prompt(
        "Content type filter (photo, clipart, lineart, face, demotivator, none): ",
        completer=content_type_completer,
        default="photo"
    )
    content_type = None if content_type.lower() == "none" else content_type.lower()
    
    # Image size filter
    size_completer = WordCompleter(['large', 'medium', 'small', 'none'])
    image_size = prompt(
        "Image size filter (large, medium, small, none): ",
        completer=size_completer,
        default="large"
    )
    image_size = None if image_size.lower() == "none" else image_size.lower()
    
    # Orientation filter
    orientation_completer = WordCompleter(['horizontal', 'vertical', 'square', 'none'])
    orientation = prompt(
        "Image orientation filter (horizontal, vertical, square, none): ",
        completer=orientation_completer,
        default="none"
    )
    orientation = None if orientation.lower() == "none" else orientation.lower()
    
    # Ask if user wants to download the images
    download = typer.confirm("Do you want to download the images?", default=True)
    
    # Ask if user wants to save URLs to file
    save_urls = typer.confirm("Do you want to save image URLs to a text file?", default=True)
    
    # Run the scraper
    typer.echo(f"\nStarting image scraper for: {search_query}")
    asyncio.run(run_scraper(
        search_query, 
        num_images,
        content_type,
        image_size,
        orientation,
        download, 
        save_urls
    ))


def main():
    """
    Main entry point
    """
    app()


if __name__ == "__main__":
    main()
