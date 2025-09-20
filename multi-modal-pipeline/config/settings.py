import os
from pathlib import Path

# Brand Guidelines
BRAND_GUIDELINES = {
    "tone": "professional, friendly",
    "keywords": ["innovation", "quality"],
    "avoid_words": ["cheap", "basic"],
    "color_palette": ["#1a73e8", "#34a853"],
    "style": "modern, clean"
}

# Model Configuration
MODEL_CONFIG = {
    "text_model": "gemini-2.5-flash",
    "image_model": "gemini-2.5-flash-image-preview",
    "temperature": 0.7,
    "max_tokens": 2048
}

# Platform Settings
PLATFORMS = {
    "linkedin": {
        "max_chars": 3000,
        "optimal_length": 1500,
        "hashtags": 5
    },
    "x": {
        "max_chars": 280,
        "optimal_length": 200,
        "hashtags": 3
    },
    "blog": {
        "min_words": 800,
        "optimal_words": 1200,
        "max_words": 2000
    }
}

# File Paths
BASE_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
IMAGES_DIR = OUTPUTS_DIR / "images"
CONTENT_DIR = OUTPUTS_DIR / "content"

# Ensure directories exist
OUTPUTS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
CONTENT_DIR.mkdir(exist_ok=True)

# API Configuration
def get_api_key():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    return api_key