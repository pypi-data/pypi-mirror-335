#!/usr/bin/env python3
"""
Spoofing configurations for Camoufox to evade detection
"""

import random
from typing import Dict, Any, List

# Common User-Agents (same as in main.py for consistency)
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

# Common Languages with Regions
LANGUAGES: List[Dict[str, str]] = [
    {"language": "en", "region": "US"},
    {"language": "en", "region": "GB"},
    {"language": "de", "region": "DE"},
    {"language": "fr", "region": "FR"},
    {"language": "es", "region": "ES"},
    {"language": "it", "region": "IT"},
    {"language": "ru", "region": "RU"},
]

# Timezone mapping to regions
TIMEZONE_MAP: Dict[str, List[str]] = {
    "US": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"],
    "GB": ["Europe/London"],
    "DE": ["Europe/Berlin"],
    "FR": ["Europe/Paris"],
    "ES": ["Europe/Madrid"],
    "IT": ["Europe/Rome"],
    "RU": ["Europe/Moscow"],
}

# Common screen resolutions
SCREEN_RESOLUTIONS: List[Dict[str, int]] = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
    {"width": 1280, "height": 720},
    {"width": 2560, "height": 1440},
]

def get_random_resolution() -> Dict[str, int]:
    """Get a random screen resolution"""
    return random.choice(SCREEN_RESOLUTIONS)

def get_random_language() -> Dict[str, str]:
    """Get a random language configuration"""
    return random.choice(LANGUAGES)

def get_random_timezone(region: str) -> str:
    """Get a random timezone based on region"""
    return random.choice(TIMEZONE_MAP.get(region, TIMEZONE_MAP["US"]))

def generate_spoofing_config() -> Dict[str, Any]:
    """
    Generate a random spoofing configuration for Camoufox
    """
    # Select random user agent
    user_agent: str = random.choice(USER_AGENTS)
    
    # Select random language/region
    lang_config: Dict[str, str] = get_random_language()
    language: str = lang_config["language"]
    region: str = lang_config["region"]
    
    # Get a random screen resolution
    resolution: Dict[str, int] = get_random_resolution()
    
    # Build the config
    config: Dict[str, Any] = {
        # Basic navigator configuration
        "navigator.userAgent": user_agent,
        "navigator.platform": "Win32" if "Windows" in user_agent else "MacIntel" if "Mac" in user_agent else "Linux x86_64",
        "navigator.language": f"{language}-{region}",
        "navigator.languages": [f"{language}-{region}", language],
        "navigator.hardwareConcurrency": random.choice([2, 4, 8, 12, 16]),
        "navigator.deviceMemory": random.choice([2, 4, 8, 16]),
        
        # Headers
        "headers.User-Agent": user_agent,
        "headers.Accept-Language": f"{language}-{region},{language};q=0.9",
        
        # Screen and window properties
        "screen.width": resolution["width"],
        "screen.height": resolution["height"],
        "screen.availWidth": resolution["width"] - random.randint(0, 60),
        "screen.availHeight": resolution["height"] - random.randint(30, 100),
        "screen.colorDepth": 24,
        "screen.pixelDepth": 24,
        
        # Window dimensions
        "window.innerWidth": resolution["width"] - random.randint(50, 150),
        "window.innerHeight": resolution["height"] - random.randint(100, 200),
        "window.outerWidth": resolution["width"] - random.randint(0, 20),
        "window.outerHeight": resolution["height"] - random.randint(0, 50),
        
        # Locale settings
        "locale:language": language,
        "locale:region": region,
        "timezone": get_random_timezone(region),
        
        # Human cursor movement
        "humanize": True,
        "humanize:minTime": 0.5,
        "humanize:maxTime": 1.5,
        "showcursor": True,
        
        # WebGL parameters - using minimal safe values
        "webGl:vendor": "Google Inc. (Intel)" if "Chrome" in user_agent else "Intel Inc.",
        "webGl:renderer": "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
        
        # Miscellaneous settings
        "pdfViewerEnabled": True,
        
        # Audio settings
        "AudioContext:sampleRate": random.choice([44100, 48000]),
        
        # Media devices
        "mediaDevices:enabled": True,
        "mediaDevices:micros": random.randint(1, 3),
        "mediaDevices:webcams": random.randint(1, 2),
        "mediaDevices:speakers": random.randint(1, 2),
        
        # Battery
        "battery:charging": True,
        "battery:level": random.uniform(0.5, 1.0),
    }
    
    return config
