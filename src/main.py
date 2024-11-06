import streamlit as st
import os # to access env variables
from dotenv import load_dotenv # load env variable from .env file 
from agents import HFInferenceLLM, DebateAgent

# Load environment variables
load_dotenv()

# Initialize Streamlit page config
st.set_page_config(
    page_title="AI Debate System",
    page_icon="🗣️",
    layout="wide"
)

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

    # Only initialize LLM and run test if button is clicked
    """
    if test_button:
        try:
            with st.spinner("Initializing LLM and testing connection..."):
                llm = HFInferenceLLM(api_token)
                test_response = llm("Hello! Please respond with a short greeting.")
                if "error" not in test_response.lower():
                    st.success("LLM connection test successful!")
                    st.info(f"Test Response: {test_response}")
                else:
                    st.error("LLM test failed. Please check your API token.")
        except Exception as e:
            st.error(f"Error initializing LLM: {str(e)}")

    st.write("Other switches to add")
"""
    # Test code for debate agent
    if test_button:
        try:
            with st.spinner("Testing debate agent..."):
                llm = HFInferenceLLM(api_token)
                
                # Test DebateAgent
                debater = DebateAgent("Pro", "in favor", llm)
                opening = debater.generate_opening_statement(
                    "Should AI be regulated?",
                    {"debate_style": "Formal", "focus_points": 3}
                )
                st.success("Debate agent test successful!")
                st.info(f"Sample opening statement: {opening}")
                
        except Exception as e:
            st.error(f"Error testing debate agent: {str(e)}")

if __name__ == "__main__":
    main()

# test streamlit run src/main.py