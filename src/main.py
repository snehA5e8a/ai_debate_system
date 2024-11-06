import streamlit as st
import os # to access env variables
from dotenv import load_dotenv # load env variable from .env file 
from agents import *

# Load environment variables
load_dotenv()

# Initialize Streamlit page config
st.set_page_config(
    page_title="AI Debate System",
    page_icon="🗣️",
    layout="wide"
)

def test_llm_connection(api_token):
    """Test the LLM connection and return detailed results"""
    try:
        llm = HFInferenceLLM(api_token)
        test_response = llm("Hello! Please respond with a short greeting.")
        
        return {
            "success": True if test_response and "error" not in test_response.lower() else False,
            "response": test_response,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "response": None,
            "error": str(e)
        }
def main():
    st.title("AI Debate System")

    # HuggingFace API setup
    api_token = st.text_input(
        "Enter your HuggingFace API token:",
        type="password",
        value=os.getenv('HUGGINGFACE_API_TOKEN', ''),
        help="Get your free token at https://huggingface.co/settings/tokens"
    )

    if not api_token:
        st.warning("Please enter your HuggingFace API token to continue")
        st.markdown("""
        To get your free API token:
        1. Go to [HuggingFace](https://huggingface.co/join)
        2. Create an account or sign in
        3. Go to Settings → Access Tokens
        4. Create a new token
        """)
        return

    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("API token configured successfully!")
        # Test button
        test_button = st.button("Test LLM Connection")

    if test_button:
        with st.spinner("Testing system..."):
            # Test LLM first
            llm_test = test_llm_connection(api_token)
            if not llm_test["success"]:
                st.error(f"LLM test failed: {llm_test['error']}")
                return
                
            st.success("LLM connection test successful!")
            st.info(f"LLM test response: {llm_test['response']}")
            
            # Proceed with debate agent test
            llm = HFInferenceLLM(api_token)
            debater = DebateAgent("Pro", "in favor", llm)
            
            parameters = {
                "debate_style": "Formal",
                "focus_points": 3
            }
            
            opening = debater.generate_opening_statement(
                "Should AI be regulated?",
                parameters
            )
            
            if "Error" in opening:
                st.error(f"Debate agent test failed: {opening}")
            else:
                st.success("Debate agent test successful!")
                st.info(f"Sample opening statement: {opening}")
if __name__ == "__main__":
    main()

# test streamlit run src/main.py