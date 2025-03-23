# Yandex Image Scraper

A command-line tool to scrape and download images from Yandex search results.

## Features
- Search for images on Yandex
- Scrape image URLs from search results
- Auto-scrolling to load more images
- Auto-clicks "Show more" button when available
- High-performance parallel downloading (50 images at once)
- Customize search parameters (content type, size, orientation)
- Save image URLs to text file

## How It Works

1. The script uses Playwright via Camoufox to open a browser window to Yandex Images
2. It searches for your query and extracts image URLs from the results
3. Automatically scrolls to load more results and clicks "Show more" when needed
4. Downloads all found images in parallel (up to 50 at once) for maximum speed
5. Saves images to a folder named after your search query

## Usage
```bash
# Install from PyPI
pip install yandex-image-scraper

# Run the tool
yandex-image-scraper

# Follow the prompts to:
# - Enter your search query
# - Specify how many images to download
# - Select content type (photo, clipart, etc.)
# - Choose image size and orientation
# - Enable/disable image downloads and URL saving
```

## Options

When running the tool, you can customize:
- **Search query**: What to search for on Yandex Images
- **Number of images**: How many images to find and download
- **Content type**: photo, clipart, lineart, face, demotivator, or none
- **Image size**: large, medium, small, or none
- **Orientation**: horizontal, vertical, square, or none

## Requirements
- Python >= 3.8

## License
GPL-3.0
