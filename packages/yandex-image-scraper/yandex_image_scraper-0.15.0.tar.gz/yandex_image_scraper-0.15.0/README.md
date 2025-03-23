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
- Browser fingerprint spoofing to avoid detection

## How It Works

1. The script uses Playwright via Camoufox to open a browser window to Yandex Images
2. Applies advanced browser fingerprint spoofing to avoid detection
3. It searches for your query and extracts image URLs from the results
4. Automatically scrolls to load more results and clicks "Show more" when needed
5. Downloads all found images in parallel (up to 25 images per batch concurrently) for maximum speed
6. Saves images to a folder named after your search query

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
# - Choose headless mode (hidden browser) or visible browser
```

## Options

When running the tool, you can customize:
- **Search query**: What to search for on Yandex Images
- **Number of images**: How many images to find and download
- **Content type**: photo, clipart, lineart, face, demotivator, or none
- **Image size**: large, medium, small, or none
- **Orientation**: horizontal, vertical, square, or none
- **Headless mode**: Run without showing browser window (faster but may require manual CAPTCHA solving)

## Anti-Detection Technology

This tool uses advanced browser fingerprint spoofing techniques to avoid detection:
- Randomized user agents, languages, and timezones
- Human-like cursor movements
- Spoofed screen and window dimensions
- WebGL renderer spoofing
- Audio context randomization
- Battery status spoofing

## Requirements
- Python >= 3.8

## License
GPL-3.0
