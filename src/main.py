import streamlit as st
import os # to access env variables
from dotenv import load_dotenv # load env variable from .env file 

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

    st.success("API token configured successfully!")
    st.write("Other switches to add")

if __name__ == "__main__":
    main()

# test streamlit run src/main.py