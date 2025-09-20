import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from config.settings import CONTENT_DIR

def save_results_to_file(results: Dict, content_request: Dict) -> str:
    # Save final results to JSON file
    
    topic = content_request.get("topic", "content").replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{topic}_{timestamp}_results.json"
    
    file_path = CONTENT_DIR / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return str(file_path)

def print_results_summary(results: Dict):
    # Print a clean summary of results to console
    
    print("\n" + "="*80)
    print("MULTI-MODAL CONTENT CREATION PIPELINE RESULTS")
    print("="*80)
    
    # Basic info
    print(f"Request: {results.get('original_request', {}).get('topic', 'N/A')}")
    print(f"Platform: {results.get('routing_decision', {}).get('content_type', 'N/A')}")
    print(f"Timestamp: {results.get('timestamp', 'N/A')}")
    
    # Quality scores
    qa_results = results.get('qa_results', {})
    print(f"\nOverall Quality Score: {qa_results.get('overall_quality_score', 'N/A')}/10")
    print(f"Approval Status: {qa_results.get('approval_status', 'N/A')}")
    
    # Content summary
    text_content = results.get('agent_outputs', {}).get('text_generator', {})
    if text_content:
        print(f"\nTitle: {text_content.get('title', 'N/A')}")
        print(f"Word Count: {text_content.get('word_count', 'N/A')}")
    
    # Image info
    image_content = results.get('agent_outputs', {}).get('image_creator', {})
    if image_content and image_content.get('success'):
        print(f"Image Generated: {image_content.get('image_path', 'N/A')}")
    
    # Files saved
    if results.get('files_saved'):
        print(f"\nResults saved to: {results['files_saved']}")
    
    print("="*80 + "\n")

async def run_agents_concurrently(agents: List, content_request: Dict, context: Dict) -> Dict:
    # Run multiple agents concurrently (Parallelization Pattern)
    
    print(f"Running {len(agents)} agents concurrently...")
    
    # Create tasks for concurrent execution
    tasks = []
    for agent_name, agent_instance in agents:
        task = asyncio.create_task(
            agent_instance.execute(content_request, context),
            name=agent_name
        )
        tasks.append((agent_name, task))
    
    # Wait for all tasks to complete
    results = {}
    for agent_name, task in tasks:
        try:
            result = await task
            results[agent_name] = result
            print(f"✓ {agent_name} completed")
        except Exception as e:
            results[agent_name] = {"error": str(e), "agent": agent_name}
            print(f"✗ {agent_name} failed: {str(e)}")
    
    return results

def create_agent_context(routing_decision: Dict, previous_outputs: Dict = None) -> Dict:
    # Create context for agents based on routing decision and previous outputs
    
    context = {
        "content_type": routing_decision.get("content_type"),
        "platform_specs": routing_decision.get("platform_specs"),
        "complexity": routing_decision.get("complexity"),
        "requires_images": routing_decision.get("requires_images"),
        "requires_seo": routing_decision.get("requires_seo")
    }
    
    if previous_outputs:
        context.update(previous_outputs)
    
    return context