import streamlit as st

# Initialize Streamlit page config
st.set_page_config(
    page_title="AI Debate System",
    page_icon="🗣️",
    layout="wide"
)

def main():
    st.title("AI Debate System")
    st.write("Initial setup - more features to be added")

    if st.button("Click me to test"):
        st.write("Button works!")

if __name__ == "__main__":
    main()

# test streamlit run src/main.py