from huggingface_hub import InferenceClient
import streamlit as st

class HFInferenceLLM:
    """Language model interface using HuggingFace Inference API"""
    def __init__(self, api_token: str):
        self.client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            token=api_token
        )
    
    def __call__(self, prompt: str) -> str:
        ''' Passing prompt via InferenceClient text generation method'''
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=180,
                temperature=0.6,  # randomness from consistency to creativity (RFL)
                repetition_penalty=1.2, # Small penalty
                return_full_text=False # No need of returning prompt 
            )
            if response is None:
                return "No response generated"
            return str(response).strip() # str response removing extra spaces 
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "Error generating response"