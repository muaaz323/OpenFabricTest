import os
import logging
from typing import Dict, Any, Optional, List
import requests

class LLMService:
    """
    Service for interacting with local LLM models (DeepSeek or Llama) using the Ollama API.
    
    This service handles prompt enhancement and creative expansion of user inputs.
    """
    
    def __init__(self, model_name: str = "deepseek-coder:latest", base_url: str = "http://localhost:11434"):
        """
        Initialize the LLM service.
        
        Args:
            model_name (str): Name of the local model to use (default: "deepseek-coder")
            base_url (str): Base URL for the Ollama API
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/generate"
        
        # Test connection to Ollama
        self._test_connection()
    
    def _test_connection(self) -> None:
        """Test the connection to the Ollama API and log result"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name") for model in models]
                
                if self.model_name not in model_names:
                    logging.warning(f"Model '{self.model_name}' not found in available models: {model_names}")
                    logging.warning(f"Please pull the model with 'ollama pull {self.model_name}'")
                else:
                    logging.info(f"Successfully connected to Ollama. Using model: {self.model_name}")
            else:
                logging.error(f"Failed to connect to Ollama API: {response.status_code}")
        except Exception as e:
            logging.error(f"Error connecting to Ollama API: {e}")
            logging.info("Please make sure Ollama is installed and running with 'ollama serve'")
    
    def enhance_prompt(self, prompt: str) -> str:
        """
        Enhance a user prompt with creative details for better image generation.
        
        Args:
            prompt (str): Original user prompt
            
        Returns:
            str: Enhanced prompt with additional creative details
        """
        system_prompt = """
        You are a creative AI assistant helping to enhance text-to-image prompts. 
        Your job is to take a simple user prompt and expand it with rich, vivid details that will 
        help an image generation system create a more compelling and detailed image.
        
        Focus on adding:
        - Visual details (textures, materials, lighting)
        - Style elements (artistic style, mood, atmosphere)
        - Composition suggestions
        
        Keep your response ONLY to the enhanced prompt text, with no explanations or other text.
        """
        
        user_message = f"Please enhance this prompt for image generation: {prompt}"
        
        enhanced_prompt = self._generate_completion(system_prompt, user_message)
        
        if not enhanced_prompt:
            logging.warning("Failed to enhance prompt, using original")
            return prompt
            
        return enhanced_prompt
    
    def analyze_memory(self, prompt: str, past_generations: List[Dict[str, Any]]) -> str:
        """
        Analyze memory to provide context-aware prompt enhancement.
        
        Args:
            prompt (str): Current user prompt
            past_generations (List[Dict[str, Any]]): Past generation records
            
        Returns:
            str: Enhanced prompt with contextual awareness
        """
        if not past_generations:
            return self.enhance_prompt(prompt)
            
        system_prompt = """
        You are a creative AI assistant with memory of past creations. Your job is to enhance 
        the current prompt based on the user's history of generations.
        
        When a user references a previous creation, understand what they're referring to and 
        incorporate relevant details from that previous creation into the new prompt.
        
        Keep your response ONLY to the enhanced prompt text, with no explanations or other text.
        """
        
        # Format past generations
        past_gen_text = "\n".join([
            f"ID: {gen['id']}, Time: {gen['timestamp']}, " 
            f"Original Prompt: '{gen['prompt']}', "
            f"Enhanced Prompt: '{gen['enhanced_prompt']}'"
            for gen in past_generations[:5]  # Only include the 5 most recent
        ])
        
        user_message = f"""
        New prompt: {prompt}
        
        Previous generations:
        {past_gen_text}
        
        Please enhance the new prompt, incorporating relevant context from previous generations if appropriate.
        """
        
        enhanced_prompt = self._generate_completion(system_prompt, user_message)
        
        if not enhanced_prompt:
            logging.warning("Failed to analyze memory, using basic enhancement")
            return self.enhance_prompt(prompt)
            
        return enhanced_prompt
    
    def _generate_completion(self, system_prompt: str, user_message: str) -> Optional[str]:
        """
        Generate a completion from the LLM.
        
        Args:
            system_prompt (str): System prompt to guide the LLM
            user_message (str): User message to process
            
        Returns:
            Optional[str]: Generated completion or None if failed
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": user_message,
                "system": system_prompt,
                "stream": False
            }
            
            response = requests.post(self.api_url, json=payload)
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                logging.error(f"LLM API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error generating LLM completion: {e}")
            return None 