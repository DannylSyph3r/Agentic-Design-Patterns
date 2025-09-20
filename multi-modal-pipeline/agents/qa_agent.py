import json
from typing import Dict, List
from agents import BaseAgent

class QualityAssuranceAgent(BaseAgent):
    # Reflection Pattern: Reviews and iteratively improves content quality
    
    def __init__(self):
        super().__init__(temperature=0.2)  # Lower temperature for consistent evaluation
    
    async def execute(self, content_request: Dict, context=None) -> Dict:
        # Review all agent outputs and provide improvement feedback
        
        all_outputs = context.get("agent_outputs", {}) if context else {}
        
        qa_prompt = f"""
        Review and evaluate all content outputs for quality and goal achievement:
        
        Original Request: {json.dumps(content_request, indent=2)}
        
        Agent Outputs:
        {json.dumps(all_outputs, indent=2)}
        
        Evaluate on these criteria:
        1. Goal Achievement (1-10): Does content meet original request?
        2. Quality Standards (1-10): Professional quality and accuracy
        3. Brand Consistency (1-10): Alignment with brand guidelines
        4. Platform Optimization (1-10): Suitable for target platform
        5. Engagement Potential (1-10): Likely to engage target audience
        
        Return JSON with:
        {{
            "overall_quality_score": number (1-10),
            "individual_scores": {{
                "goal_achievement": number,
                "quality_standards": number,
                "brand_consistency": number,
                "platform_optimization": number,
                "engagement_potential": number
            }},
            "strengths": ["what works well"],
            "weaknesses": ["areas needing improvement"],
            "specific_feedback": {{
                "text_content": ["feedback for text"],
                "image_content": ["feedback for images"],
                "seo_content": ["feedback for SEO"],
                "brand_compliance": ["feedback for brand"]
            }},
            "improvement_required": true/false,
            "priority_fixes": ["most important changes"],
            "approval_status": "approved|needs_revision|rejected",
            "iteration_suggestions": ["how to improve in next iteration"]
        }}
        
        Be constructive and specific in feedback.
        """
        
        try:
            response = await self.model.generate_content_async(
                qa_prompt,
                generation_config=self._create_generation_config()
            )
            
            result = json.loads(response.text.strip())
            result["agent"] = "qa_agent"
            
            return result
            
        except Exception as e:
            return {
                "agent": "qa_agent",
                "error": str(e),
                "overall_quality_score": 5,
                "improvement_required": True,
                "approval_status": "needs_revision",
                "priority_fixes": ["Manual quality review needed due to QA error"]
            }
    
    async def should_iterate(self, qa_results: Dict, min_score: float = 7.0) -> bool:
        # Determine if another iteration is needed based on QA results
        
        overall_score = qa_results.get("overall_quality_score", 0)
        improvement_required = qa_results.get("improvement_required", True)
        
        return overall_score < min_score or improvement_required