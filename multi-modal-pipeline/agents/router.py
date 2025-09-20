import json
from typing import Dict, List
from agents import BaseAgent
from config.settings import PLATFORMS, BRAND_GUIDELINES

class ContentRouterAgent(BaseAgent):
    # Routing Pattern: Analyzes requests and determines which agents to invoke
    
    def __init__(self):
        # Lower temperature for consistent routing
        super().__init__(temperature=0.3)  
    
    async def execute(self, content_request: Dict, context=None) -> Dict:
        # Analyze request and determine routing strategy
        
        routing_prompt = f"""
        Analyze this content request and determine which agents should be involved:
        
        Request: {json.dumps(content_request, indent=2)}
        
        Available Agents:
        - text_generator: Creates written content
        - image_creator: Generates custom images
        - seo_optimizer: Optimizes for search engines
        - brand_validator: Ensures brand compliance
        
        Platform Capabilities: {json.dumps(PLATFORMS, indent=2)}
        Brand Guidelines: {json.dumps(BRAND_GUIDELINES, indent=2)}
        
        Return a JSON object with:
        {{
            "required_agents": ["agent1", "agent2"],
            "content_type": "blog|linkedin|x",
            "complexity": "simple|medium|complex",
            "requires_images": true/false,
            "requires_seo": true/false,
            "execution_order": "parallel|sequential",
            "platform_specs": {{platform-specific requirements}}
        }}
        
        Be precise and only include necessary agents.
        """
        
        try:
            response = await self.model.generate_content_async(
                routing_prompt,
                generation_config=self._create_generation_config()
            )
            
            # Parse the JSON response
            routing_decision = json.loads(response.text.strip())
            
            # Validate and ensure required agents are included
            self._validate_routing_decision(routing_decision, content_request)
            
            return routing_decision
            
        except Exception as e:
            # Fallback routing for safety
            return self._fallback_routing(content_request)
    
    def _validate_routing_decision(self, decision: Dict, request: Dict):
        # Validate routing decision and add missing agents if needed
        
        # Always include brand_validator
        if "brand_validator" not in decision["required_agents"]:
            decision["required_agents"].append("brand_validator")
        
        # Add text_generator if content creation is needed
        if "text_generator" not in decision["required_agents"]:
            decision["required_agents"].append("text_generator")
    
    def _fallback_routing(self, content_request: Dict) -> Dict:
        # Fallback routing strategy if analysis fails
        return {
            "required_agents": ["text_generator", "brand_validator"],
            "content_type": "blog",
            "complexity": "medium",
            "requires_images": False,
            "requires_seo": False,
            "execution_order": "parallel",
            "platform_specs": PLATFORMS["blog"]
        }