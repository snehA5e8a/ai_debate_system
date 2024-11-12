from langchain_core.language_models import BaseLLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import Generation, LLMResult
from huggingface_hub import InferenceClient
from typing import Any, List, Optional

class HuggingFaceInferenceLLM(BaseLLM):
    """LangChain wrapper for HuggingFace Inference API"""
    
    client: InferenceClient
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"
    
    def __init__(self, api_token: str):
        super().__init__()
        self.client = InferenceClient(model=self.model_name, token=api_token)
        
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Execute the LLM call."""
        response = self.client.text_generation(
            prompt,
            max_new_tokens=180,
            temperature=0.6,
            repetition_penalty=1.2,
            return_full_text=False
        )
        return str(response).strip()
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "huggingface_inference"