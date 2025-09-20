import json
from typing import Dict
from agents import BaseAgent
from config.settings import BRAND_GUIDELINES

class BrandValidatorAgent(BaseAgent):
    # Validates content against brand guidelines and compliance requirements
    
    async def execute(self, content_request: Dict, context=None) -> Dict:
        # Validate all content against brand guidelines
        
        text_content = context.get("text_content", {}) if context else {}
        seo_content = context.get("seo_content", {}) if context else {}
        image_content = context.get("image_content", {}) if context else {}
        
        validation_prompt = f"""
        Validate this content against brand guidelines:
        
        Brand Guidelines: {json.dumps(BRAND_GUIDELINES, indent=2)}
        
        Content to Validate:
        Text: {json.dumps(text_content, indent=2)}
        SEO: {json.dumps(seo_content, indent=2)}
        Image: {json.dumps(image_content, indent=2)}
        
        Check for:
        1. Tone consistency with brand voice
        2. Proper use of brand keywords
        3. Avoidance of prohibited words
        4. Overall brand alignment
        5. Professional quality standards
        
        Return JSON with:
        {{
            "brand_compliance_score": number (1-10),
            "tone_analysis": {{
                "current_tone": "detected tone",
                "alignment_score": number (1-10),
                "recommendations": ["specific improvements"]
            }},
            "keyword_analysis": {{
                "brand_keywords_used": ["found keywords"],
                "missing_keywords": ["should include"],
                "prohibited_words_found": ["avoid these"]
            }},
            "overall_assessment": "detailed analysis",
            "approved": true/false,
            "required_changes": ["specific changes needed"],
            "strengths": ["what works well"]
        }}
        
        Be thorough and specific in your analysis.
        """
        
        try:
            response = await self.model.generate_content_async(
                validation_prompt,
                generation_config=self._create_generation_config()
            )
            
            result = json.loads(response.text.strip())
            result["agent"] = "brand_validator"
            
            return result
            
        except Exception as e:
            return {
                "agent": "brand_validator",
                "error": str(e),
                "brand_compliance_score": 5,
                "approved": False,
                "required_changes": ["Manual brand review needed due to validation error"]
            }