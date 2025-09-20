from io import BytesIO
from PIL import Image
from datetime import datetime
from typing import Dict
import google.generativeai as genai
from agents import BaseAgent
from config.settings import MODEL_CONFIG, BRAND_GUIDELINES, IMAGES_DIR

class ImageCreatorAgent(BaseAgent):
    # Generates images using Gemini 2.5 Flash Image model
    
    def __init__(self):
        # Use the specific image model
        super().__init__(model_name=MODEL_CONFIG["image_model"])
    
    async def execute(self, content_request: Dict, context=None) -> Dict:
        """Generate custom images based on content requirements"""
        
        # Extract content context for image generation
        text_content = context.get("text_content", {}) if context else {}
        platform = context.get("content_type", "blog") if context else "blog"
        
        # Create image prompt based on content and brand guidelines
        image_prompt = self._build_image_prompt(content_request, text_content, platform)
        
        try:
            # Generate image using Gemini 2.5 Flash Image
            response = await self.model.generate_content_async(
                contents=[image_prompt],
                generation_config=self._create_generation_config()
            )
            
            # Extract image data from response
            image_data = None
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data
                    break
            
            if image_data:
                # Save image locally
                image_path = self._save_image(image_data, content_request)
                
                return {
                    "agent": "image_creator",
                    "image_path": str(image_path),
                    "prompt_used": image_prompt,
                    "platform": platform,
                    "success": True
                }
            else:
                return {
                    "agent": "image_creator",
                    "error": "No image data in response",
                    "success": False
                }
                
        except Exception as e:
            return {
                "agent": "image_creator",
                "error": str(e),
                "success": False
            }
    
    def _build_image_prompt(self, content_request: Dict, text_content: Dict, platform: str) -> str:
        # Build detailed image generation prompt
        
        topic = content_request.get("topic", "business content")
        style = BRAND_GUIDELINES["style"]
        colors = ", ".join(BRAND_GUIDELINES["color_palette"])
        
        prompt = f"""
        Create a professional, high-quality image for {platform} content about: {topic}
        
        Style Requirements:
        - {style} design aesthetic
        - Brand colors: {colors}
        - Professional and engaging
        - Suitable for business/professional audience
        - Modern, clean composition
        
        Content Context: {text_content.get('title', topic)}
        
        Specifications:
        - High resolution and quality
        - Clear focal point
        - Appropriate for social media sharing
        - Visually appealing and professional
        - On-brand visual elements
        
        Create an image that complements the content and attracts audience attention.
        """
        
        return prompt.strip()
    
    def _save_image(self, image_data: bytes, content_request: Dict) -> str:
        # Save generated image to local storage 
        
        # Create filename based on topic and timestamp
        topic = content_request.get("topic", "content").replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{topic}_{timestamp}.png"
        
        image_path = IMAGES_DIR / filename
        
        try:
            # Convert bytes to PIL Image and save
            image_bytes = BytesIO(image_data)
            image = Image.open(image_bytes)
            image.save(image_path, "PNG")
            
            return image_path
            
        except Exception as e:
            raise Exception(f"Failed to save image: {str(e)}")