import json
from typing import Dict
from agents import BaseAgent
from config.settings import BRAND_GUIDELINES, PLATFORMS

class TextGeneratorAgent(BaseAgent):
    # Generates text content based on requirements and platform specifications
    
    async def execute(self, content_request: Dict, context=None) -> Dict:
        # Generate text content based on request and routing context
        
        platform = context.get("content_type", "blog") if context else "blog"
        platform_specs = context.get("platform_specs", PLATFORMS[platform]) if context else PLATFORMS[platform]
        
        generation_prompt = f"""
        Create high-quality content based on these specifications:
        
        Content Request: {json.dumps(content_request, indent=2)}
        Platform: {platform}
        Platform Specifications: {json.dumps(platform_specs, indent=2)}
        Brand Guidelines: {json.dumps(BRAND_GUIDELINES, indent=2)}
        
        Requirements:
        1. Follow the brand tone: {BRAND_GUIDELINES['tone']}
        2. Include brand keywords naturally: {BRAND_GUIDELINES['keywords']}
        3. Avoid these words: {BRAND_GUIDELINES['avoid_words']}
        4. Adapt content length to platform requirements
        5. Make it engaging and valuable for the target audience
        
        Return a JSON object with:
        {{
            "title": "Compelling title",
            "content": "Main content body",
            "summary": "Brief summary",
            "word_count": number,
            "hashtags": ["relevant", "hashtags"],
            "call_to_action": "Clear CTA"
        }}
        
        Ensure content is original, valuable, and platform-optimized.
        """
        
        try:
            response = await self.model.generate_content_async(
                generation_prompt,
                generation_config=self._create_generation_config()
            )
            
            result = json.loads(response.text.strip())
            result["agent"] = "text_generator"
            result["platform"] = platform
            
            return result
            
        except Exception as e:
            return {
                "agent": "text_generator",
                "error": str(e),
                "title": "Content Generation Failed",
                "content": "Unable to generate content at this time.",
                "platform": platform
            }