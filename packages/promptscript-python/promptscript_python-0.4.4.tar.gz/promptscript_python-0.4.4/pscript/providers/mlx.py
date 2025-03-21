import json
import logging
import mlx_lm
from typing import Optional, Type, List, Dict, Any
from pydantic import BaseModel
from .base import BaseProvider
from ..utils import validate_type

logger = logging.getLogger(__name__)

class MLXProvider(BaseProvider):
    """MLX-specific provider implementation using Apple's mlx-lm library"""
    
    def _clean_prompt(self, prompt: str) -> str:
        """Clean prompt by explicitly removing indentation"""
        lines = prompt.splitlines()
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return '\n'.join(cleaned_lines)
    
    def call_model(self, 
                messages: List[Dict[str, Any]], 
                images: Optional[List[Dict[str, Any]]] = None,
                response_format: Optional[Type[BaseModel]] = None,
                functions: Optional[List[Dict[str, Any]]] = None) -> Any:
        """
        Call MLX model with given messages.
        """
        try:
            # Remove only the provider prefix (mlx/), keeping the rest of the path
            model_id = '/'.join(self.model_id.split('/')[1:])
            
            # Load model and tokenizer
            logger.debug(f"Loading MLX model: {model_id}")
            model, tokenizer = mlx_lm.load(model_id)
            
            # Extract the user prompt
            prompt = None
            for msg in messages:
                if msg["role"].lower() == "user":
                    prompt = msg.get("content", "")
                    break
                    
            if prompt is None:
                raise ValueError("No user message found in prompt")
                
            # Clean the prompt
            logger.debug(f"Raw prompt before cleaning:\n{prompt}")
            prompt = self._clean_prompt(prompt)
            logger.debug(f"Raw prompt after cleaning:\n{prompt}")

            # Check for chat template support
            if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template is not None:
                # Format messages as required by the chat template
                chat_messages = [{"role": "user", "content": prompt}]
                prompt = tokenizer.apply_chat_template(
                    chat_messages, tokenize=False, add_generation_prompt=True
                )
                logger.debug(f"Prompt after applying chat template:\n{prompt}")

            # Generate response
            response = mlx_lm.generate(
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                max_tokens=self.model_config.parameters.max_tokens_range[1],
                temp=float(self.model_config.parameters.temperature_range[0])
            )
            
            content = response.strip()
            logger.debug(f"Raw response:\n{content}")
            
            # If a structured response is expected, try to parse as JSON
            if response_format and response_format is not str:
                try:
                    parsed = json.loads(content)
                    return validate_type(parsed, response_format)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Model response is not valid JSON: {e}\nResponse was: {content}")
            
            return content
                
        except Exception as e:
            logger.error(f"Error in MLX model call: {e}")
            raise