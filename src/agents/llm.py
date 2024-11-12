from huggingface_hub import InferenceClient
import streamlit as st
from .utils import clean_response

class HFInferenceLLM:
    """Language model interface using HuggingFace Inference API"""
    def __init__(self, api_token: str):
        self.client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            token=api_token
        )
    
    def __call__(self, prompt: str) -> str:
        try:
            # Increase max_new_tokens to handle longer responses
            response = self.client.text_generation(
                prompt,
                max_new_tokens=256,  # Increased from 180
                temperature=0.6,
                repetition_penalty=1.2,
                return_full_text=False
            )
            
            if response is None:
                return "No response generated"
                
            # Clean the response
            clean_resp = clean_response(str(response))
            
            return clean_resp
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "Error generating response"