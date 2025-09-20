import google.generativeai as genai
from abc import ABC, abstractmethod
from config.settings import get_api_key, MODEL_CONFIG

# Configure the API
genai.configure(api_key=get_api_key())

class BaseAgent(ABC):
    # Base class for all agents in the pipeline
    
    def __init__(self, model_name=None, temperature=None):
        self.model_name = model_name or MODEL_CONFIG["text_model"]
        self.temperature = temperature or MODEL_CONFIG["temperature"]
        self.model = genai.GenerativeModel(model_name=self.model_name)
    
    @abstractmethod
    async def execute(self, content_request, context=None):
        # Execute the agent's specific task
        pass
    
    def _create_generation_config(self, temperature=None):
        # Create generation config for the model
        return genai.types.GenerationConfig(
            temperature=temperature or self.temperature,
            max_output_tokens=MODEL_CONFIG["max_tokens"]
        )