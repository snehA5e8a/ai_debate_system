import streamlit as st
import os
from dotenv import load_dotenv
from typing import Dict
from langchain.callbacks import StreamlitCallbackHandler

from config import DebateConfig, DebateStyle
from llm import HuggingFaceInferenceLLM
from debate_system import DebateSystem

# Load environment variables
load_dotenv()

def render_fact_check(check_result: Dict):
    """Render fact checking results"""
    status_color = {
        'Highly Accurate': 'green',
        'Moderately Accurate': 'yellow',
        'Low Accuracy': 'orange',
        'Unverified': 'red'
    }
    
    st.markdown(
        f"<div style='padding:10px;background-color:{status_color.get(check_result['overall_accuracy'], 'gray')};'>"
        f"Overall Accuracy: {check_result['overall_accuracy']}</div>",
        unsafe_allow_html=True
    )
    
    with st.expander("Detailed Analysis"):
        for detail in check_result['details']:
            st.write(f"Claim: {detail['claim']}")
            st.write(f"Status: {detail['status']}")
            st.write(f"Confidence: {detail['confidence']:.2f}")
            st.write(f"Reasoning: {detail['reasoning']}")
            st.markdown("---")

def main():
    st.set_page_config(
        page_title="LangChain Debate System",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("LangChain Debate System")
    
    # Sidebar configuration
    st.sidebar.title("Debate Parameters")
    
    config = DebateConfig(
        debate_rounds=st.sidebar.slider(
            "Number of Exchange Rounds:",
            min_value=1,
            max_value=5,
            value=2
        ),
        focus_points=st.sidebar.number_input(
            "Points per Argument:",
            min_value=1,
            max_value=5,
            value=3
        ),
        show_thinking=st.sidebar.checkbox(
            "Show Agent Thinking Process",
            value=True
        ),
        real_time_fact_check=st.sidebar.checkbox(
            "Enable Real-time Fact Checking",
            value=True
        ),
        style=DebateStyle(
            st.sidebar.selectbox(
                "Debate Style:",
                [style.value for style in DebateStyle]
            )
        )
    )
    
    # HuggingFace API setup
    api_token = st.text_input(
        "Enter your HuggingFace API token:",
        type="password",
        value=os.getenv('HUGGINGFACE_API_TOKEN', ''),
        help="Get your token at https://huggingface.co/settings/tokens"
    )
    
    if not api_token:
        st.warning("Please enter your HuggingFace API token to continue")
        return
    
    # Topic selection
    topic_options = [
        "Is Malayalam movie industry the best in India?",
        "Should artificial intelligence be regulated?",
        "Is a Career Change After 30 a Wise Decision?",
        "Is it ok not to dive deep to programming as AI Agents are here to help",
        "Should remote work become the standard for office jobs?",
        "Custom topic"
    ]
    
    topic_selection = st.selectbox("Select debate topic:", topic_options)
    if topic_selection == "Custom topic":
        topic = st.text_input("Enter your custom topic:")
    else:
        topic = topic_selection
    
    if st.button("Start Debate") and topic:
        with st.spinner("Initializing debate..."):
            try:
                # Initialize LLM with streaming callback
                callbacks = [StreamlitCallbackHandler(st.container())]
                llm = HuggingFaceInferenceLLM(api_token)
                
                # Initialize debate system
                debate = DebateSystem(llm, config)
                
                # Run debate
                debate_log = debate.run_debate(topic)
                
                # Display debate content
                for event in debate_log:
                    if event["type"] == "ERROR":
                        st.error(event["content"])
                        break
                        
                    if event["type"] == "FACT_CHECK":
                        render_fact_check(eval(event["content"]))
                    else:
                        st.markdown(f"**{event['type']}**: {event['content']}")
                    
                    if config.show_thinking and "metadata" in event:
                        with st.expander("Thinking Process"):
                            st.write(event["metadata"])
                    
                    st.markdown("---")
                
                # Display analytics
                analytics = debate.get_analytics()
                st.sidebar.markdown("### Debate Analytics")
                st.sidebar.write("Duration:", f"{analytics['duration']:.1f}s")
                st.sidebar.write("Interventions:", analytics['interventions'])
                st.sidebar.write("Fact Checks:", analytics['fact_checks'])
                
                # Create debate transcript
                transcript = "\n\n".join([
                    f"{event['type']}: {event['content']}"
                    for event in debate_log
                    if event["type"] != "ERROR"
                ])
                
                st.download_button(
                    label="Download Debate Transcript",
                    data=transcript,
                    file_name="debate_transcript.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()