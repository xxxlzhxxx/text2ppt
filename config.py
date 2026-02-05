"""
Configuration module for Text2PPT project.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
ARK_API_KEY = os.environ.get("ARK_API_KEY")
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# Model Endpoints
LLM_ENDPOINT = os.environ.get("LLM_ENDPOINT", "ep-xxxxxxxxxx")  # Seed 2.0
IMAGE_ENDPOINT = os.environ.get("IMAGE_ENDPOINT", "ep-xxxxxxxxxx")  # Seadream 4.5

# Output directories
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")

# Ensure output directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)

# PPT Configuration
PPT_WIDTH_INCHES = 13.333  # Standard widescreen 16:9
PPT_HEIGHT_INCHES = 7.5
SLIDE_WIDTH = PPT_WIDTH_INCHES  # Alias for convenience
SLIDE_HEIGHT = PPT_HEIGHT_INCHES  # Alias for convenience

# Image generation settings
IMAGE_RATIO = "16:9"
IMAGE_SIZE = "1920x1080"
