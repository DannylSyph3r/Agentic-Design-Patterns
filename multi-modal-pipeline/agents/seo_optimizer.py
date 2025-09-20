import json
from typing import Dict
from agents import BaseAgent

class SEOOptimizerAgent(BaseAgent):
    # Optimizes content for search engines and platform discoverability
    
    async def execute(self, content_request: Dict, context=None) -> Dict:
        # Analyze and optimize content for SEO
        
        text_content = context.get("text_content", {}) if context else {}
        platform = context.get("content_type", "blog") if context else "blog"
        
        seo_prompt = f"""
        Analyze and optimize this content for SEO and platform discoverability:
        
        Original Content: {json.dumps(text_content, indent=2)}
        Platform: {platform}
        Topic: {content_request.get('topic', 'general')}
        
        Provide SEO optimization recommendations and enhanced elements:
        
        Return JSON with:
        {{
            "seo_score": number (1-10),
            "optimized_title": "SEO-friendly title",
            "meta_description": "Compelling meta description (150-160 chars)",
            "keywords": ["primary", "secondary", "long-tail"],
            "optimized_hashtags": ["#relevant", "#trending"],
            "content_improvements": ["specific suggestions"],
            "readability_score": number (1-10),
            "engagement_factors": ["elements that increase engagement"]
        }}
        
        Focus on:
        1. Keyword optimization without keyword stuffing
        2. Platform-specific optimization
        3. User engagement factors
        4. Discoverability improvements
        """
        
        try:
            response = await self.model.generate_content_async(
                seo_prompt,
                generation_config=self._create_generation_config()
            )
            
            result = json.loads(response.text.strip())
            result["agent"] = "seo_optimizer"
            result["platform"] = platform
            
            return result
            
        except Exception as e:
            return {
                "agent": "seo_optimizer",
                "error": str(e),
                "seo_score": 5,
                "platform": platform,
                "optimized_title": text_content.get("title", "Optimized Title"),
                "meta_description": "SEO optimization failed - manual review needed."
            }