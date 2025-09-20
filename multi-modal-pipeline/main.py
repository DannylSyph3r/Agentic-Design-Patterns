import asyncio
import json
from datetime import datetime
from typing import Dict

# Import all agents
from agents.router import ContentRouterAgent
from agents.text_generator import TextGeneratorAgent
from agents.image_creator import ImageCreatorAgent
from agents.seo_optimizer import SEOOptimizerAgent
from agents.brand_validator import BrandValidatorAgent
from agents.qa_agent import QualityAssuranceAgent

# Import utilities
from utils.helpers import (
    run_agents_concurrently, 
    create_agent_context, 
    save_results_to_file, 
    print_results_summary
)

class MultiModalContentPipeline:
    """
    Multi-Modal Content Creation Pipeline implementing three agentic patterns:
    1. Routing: Intelligent task delegation
    2. Parallelization: Concurrent agent execution
    3. Reflection: Iterative quality improvement
    """
    
    def __init__(self):
        # Initialize all agents
        self.router = ContentRouterAgent()
        self.agents = {
            "text_generator": TextGeneratorAgent(),
            "image_creator": ImageCreatorAgent(),
            "seo_optimizer": SEOOptimizerAgent(),
            "brand_validator": BrandValidatorAgent()
        }
        self.qa_agent = QualityAssuranceAgent()
        self.max_iterations = 2  # Prevent infinite loops
    
    async def process_content_request(self, content_request: Dict) -> Dict:
        """Main pipeline orchestrator implementing all three patterns"""
        
        start_time = datetime.now()
        print(f"🚀 Starting Multi-Modal Content Pipeline at {start_time}")
        print(f"Request: {content_request}")
        
        # PATTERN 1: ROUTING - Analyze request and determine execution strategy
        print("\n📋 ROUTING PATTERN: Analyzing request...")
        routing_decision = await self.router.execute(content_request)
        print(f"Routing Decision: {json.dumps(routing_decision, indent=2)}")
        
        # Track all results
        all_results = {
            "original_request": content_request,
            "routing_decision": routing_decision,
            "timestamp": start_time.isoformat(),
            "iterations": []
        }
        
        # PATTERN 3: REFLECTION - Iterative improvement loop
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n🔄 ITERATION {iteration}")
            
            # PATTERN 2: PARALLELIZATION - Run required agents concurrently
            print(f"\n⚡ PARALLELIZATION PATTERN: Running agents concurrently...")
            agent_outputs = await self._run_required_agents(
                content_request, 
                routing_decision, 
                all_results.get("previous_outputs", {})
            )
            
            # Collect all outputs for QA review
            context_for_qa = {
                "agent_outputs": agent_outputs,
                "content_type": routing_decision.get("content_type"),
                "iteration": iteration
            }
            
            # PATTERN 3: REFLECTION - Quality review and feedback
            print(f"\n🔍 REFLECTION PATTERN: Quality assurance review...")
            qa_results = await self.qa_agent.execute(content_request, context_for_qa)
            
            # Store iteration results
            iteration_results = {
                "iteration": iteration,
                "agent_outputs": agent_outputs,
                "qa_results": qa_results,
                "timestamp": datetime.now().isoformat()
            }
            all_results["iterations"].append(iteration_results)
            
            # Check if we need another iteration
            should_iterate = await self.qa_agent.should_iterate(qa_results)
            
            print(f"QA Score: {qa_results.get('overall_quality_score', 'N/A')}/10")
            print(f"Status: {qa_results.get('approval_status', 'N/A')}")
            
            if not should_iterate or qa_results.get('approval_status') == 'approved':
                print("✅ Content approved - pipeline complete!")
                break
            elif iteration < self.max_iterations:
                print("🔄 Quality below threshold - preparing next iteration...")
                all_results["previous_outputs"] = agent_outputs
            else:
                print("⚠️ Max iterations reached - finalizing current version")
        
        # Finalize results
        final_iteration = all_results["iterations"][-1]
        all_results.update({
            "final_outputs": final_iteration["agent_outputs"],
            "qa_results": final_iteration["qa_results"],
            "total_iterations": iteration,
            "completion_time": datetime.now().isoformat()
        })
        
        # Save and display results
        file_path = save_results_to_file(all_results, content_request)
        all_results["files_saved"] = file_path
        
        print_results_summary(all_results)
        
        return all_results
    
    async def _run_required_agents(self, content_request: Dict, routing_decision: Dict, previous_outputs: Dict) -> Dict:
        """Run required agents based on routing decision"""
        
        required_agents = routing_decision.get("required_agents", [])
        execution_order = routing_decision.get("execution_order", "parallel")
        
        # Create context for agents
        context = create_agent_context(routing_decision, previous_outputs)
        
        if execution_order == "parallel":
            # Run agents concurrently
            agent_instances = [(name, self.agents[name]) for name in required_agents if name in self.agents]
            return await run_agents_concurrently(agent_instances, content_request, context)
        else:
            # Sequential execution (fallback)
            results = {}
            for agent_name in required_agents:
                if agent_name in self.agents:
                    print(f"Running {agent_name}...")
                    result = await self.agents[agent_name].execute(content_request, context)
                    results[agent_name] = result
                    # Update context with new results
                    context[f"{agent_name}_content"] = result
            return results

# Example usage and test function
async def main():
    """Example usage of the Multi-Modal Content Pipeline"""
    
    # Example content request
    sample_request = {
        "topic": "AI in Healthcare: Transforming Patient Care",
        "target_audience": "healthcare professionals",
        "platform": "linkedin",
        "content_type": "article",
        "include_images": True,
        "tone": "professional, informative",
        "key_points": [
            "AI diagnostics accuracy",
            "Patient data privacy",
            "Cost reduction benefits",
            "Implementation challenges"
        ]
    }
    
    # Create and run pipeline
    pipeline = MultiModalContentPipeline()
    results = await pipeline.process_content_request(sample_request)
    
    print(f"\n🎉 Pipeline completed successfully!")
    print(f"Results saved to: {results.get('files_saved')}")

if __name__ == "__main__":
    asyncio.run(main())