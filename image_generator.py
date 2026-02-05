"""
Image Generator Module - Handles image generation using Seadream 4.5.
Uses OpenAI-compatible API for Volcengine Ark.
"""
import os
import time
import base64
import requests
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import ARK_API_KEY, ARK_BASE_URL, IMAGE_ENDPOINT, IMAGES_DIR


class ImageGenerator:
    """Client for generating images using Seadream 4.5 text-to-image model."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=ARK_API_KEY,
            base_url=ARK_BASE_URL
        )
        self.endpoint = IMAGE_ENDPOINT

    def generate_image(self, prompt: str, output_filename: str) -> Optional[str]:
        """
        Generate a single image from a text prompt.
        
        Args:
            prompt: Text prompt describing the image to generate
            output_filename: Name for the output file (without extension)
            
        Returns:
            Path to the saved image file, or None if generation failed
        """
        print(f"Generating image: {output_filename}", flush=True)
        print(f"Prompt: {prompt[:100]}...", flush=True)
        
        try:
            # Use with_raw_response to get headers including request ID
            raw_response = self.client.images.with_raw_response.generate(
                model=self.endpoint,
                prompt=prompt,
                n=1,
                size="2560x1440",  # Higher resolution for Seadream 4.5 (min 3686400 pixels)
                response_format="b64_json",
                extra_body={
                    "watermark": False  # Disable AI watermark
                }
            )
            
            # Extract request ID from headers
            request_id = raw_response.headers.get('x-request-id', 'N/A')
            print(f"[ImageGen] Request ID: {request_id}", flush=True)
            print(f"[ImageGen] Model: {self.endpoint}", flush=True)
            
            # Parse the response
            response = raw_response.parse()
            
            if response.data and len(response.data) > 0:
                image_data = response.data[0]
                
                # Handle base64 encoded image
                if hasattr(image_data, 'b64_json') and image_data.b64_json:
                    return self._save_base64_image(image_data.b64_json, output_filename)
                elif hasattr(image_data, 'url') and image_data.url:
                    return self._download_and_save_image(image_data.url, output_filename)
            
            print("No image data in response", flush=True)
            return None
                    
        except Exception as e:
            print(f"Error generating image: {e}", flush=True)
            # Try alternative method using raw API call
            return self._generate_image_raw_api(prompt, output_filename)

    def _generate_image_raw_api(self, prompt: str, output_filename: str) -> Optional[str]:
        """
        Alternative method using raw HTTP API call for image generation.
        Some Volcengine models may not follow OpenAI's exact API format.
        """
        try:
            headers = {
                "Authorization": f"Bearer {ARK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Try visual generation endpoint
            url = f"{ARK_BASE_URL}/images/generations"
            payload = {
                "model": self.endpoint,
                "prompt": prompt,
                "n": 1,
                "size": "2560x1440",
                "response_format": "b64_json",
                "watermark": False  # Disable AI watermark
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    b64_data = data["data"][0].get("b64_json") or data["data"][0].get("image")
                    if b64_data:
                        return self._save_base64_image(b64_data, output_filename)
                    
                    url_data = data["data"][0].get("url")
                    if url_data:
                        return self._download_and_save_image(url_data, output_filename)
            else:
                print(f"Raw API call failed: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"Raw API call error: {e}")
            
        return None

    def _download_and_save_image(self, url: str, output_filename: str) -> Optional[str]:
        """
        Download image from URL and save to file.
        """
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Determine file extension from content type
            content_type = response.headers.get('content-type', 'image/png')
            ext = 'png' if 'png' in content_type else 'jpg'
            
            filepath = os.path.join(IMAGES_DIR, f"{output_filename}.{ext}")
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Image saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

    def _save_base64_image(self, b64_data: str, output_filename: str) -> Optional[str]:
        """
        Decode base64 image data and save to file.
        """
        try:
            # Remove data URL prefix if present
            if ',' in b64_data:
                b64_data = b64_data.split(',')[1]
            
            image_bytes = base64.b64decode(b64_data)
            
            # Detect image format from magic bytes
            ext = 'png'
            if image_bytes[:3] == b'\xff\xd8\xff':
                ext = 'jpg'
            
            filepath = os.path.join(IMAGES_DIR, f"{output_filename}.{ext}")
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            print(f"Image saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving base64 image: {e}")
            return None

    def generate_slides_images(self, slides: List[Dict[str, Any]], batch_name: str = "ppt") -> List[str]:
        """
        Generate images for all slides.
        
        Args:
            slides: List of slide dictionaries containing image_prompt
            batch_name: Prefix for output filenames
            
        Returns:
            List of paths to generated images
        """
        image_paths = []
        
        for i, slide in enumerate(slides):
            slide_num = slide.get('slide_number', i + 1)
            prompt = slide.get('image_prompt', '')
            
            if not prompt:
                print(f"Warning: No image prompt for slide {slide_num}")
                continue
            
            output_filename = f"{batch_name}_slide_{slide_num:02d}"
            image_path = self.generate_image(prompt, output_filename)
            
            if image_path:
                image_paths.append(image_path)
                slide['image_path'] = image_path
            else:
                print(f"Warning: Failed to generate image for slide {slide_num}")
        
        return image_paths


def test_image_generator():
    """Test function for image generator."""
    generator = ImageGenerator()
    
    test_prompt = """Professional PPT cover slide with title 'AI in Healthcare' in large bold white font centered,
    subtitle 'The Future of Medicine' below in smaller font,
    modern blue gradient background with abstract medical icons and DNA helix graphics,
    clean minimalist corporate design, high quality 4K resolution, business presentation style"""
    
    result = generator.generate_image(test_prompt, "test_slide")
    
    if result:
        print(f"\nSuccess! Image saved to: {result}")
    else:
        print("\nFailed to generate test image")
    
    return result


if __name__ == "__main__":
    test_image_generator()
