from huggingface_hub import InferenceClient
import streamlit as st

class HFInferenceLLM:
    """Language model interface using HuggingFace Inference API"""
    def __init__(self, api_token: str):
        self.client = InferenceClient(
            model="HuggingFaceH4/zephyr-7b-beta",
            token=api_token
        )
    
    def __call__(self, prompt: str) -> str:
        ''' Passing prompt via InferenceClient text generation method'''
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=256,
                temperature=0.7,  # randomness from consistency to creativity (RFL)
                repetition_penalty=1.1, # Small penalty
                return_full_text=False # No need of returning prompt 
            )
            if response is None:
                return "No response generated"
            return str(response).strip() # str response removing extra spaces 
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "Error generating response"