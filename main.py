import streamlit as st
import os
from dotenv import load_dotenv
from src.agents.llm import HFInferenceLLM
from src.agents.debate_system import DebateSystem

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
    
    # Sidebar for debate parameters
    st.sidebar.title("Debate Parameters")
    
    parameters = {
        'debate_style': st.sidebar.selectbox(
            "Debate Style:",
            ["Formal", "Casual", "Academic"]
        ),
        'debate_rounds': st.sidebar.slider(
            "Number of Exchange Rounds:",
            min_value=1,
            max_value=5,
            value=2
        ),
        'focus_points': st.sidebar.number_input(
            "Points per Argument:",
            min_value=1,
            max_value=5,
            value=3
        ),
        'fact_checking': st.sidebar.checkbox(
            "Enable Fact Checking",
            value=True
        ),
        'show_thinking': st.sidebar.checkbox(
            "Show Agent Thinking Process",
            value=True
        )
    }
    
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
    
    # Advanced Settings Expander
    with st.expander("Advanced Debate Settings"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Agent Behavior")
            agent_strategy = st.selectbox(
                "Agent Strategy:",
                ["Balanced", "Analytical", "Persuasive"]
            )
            response_length = st.select_slider(
                "Response Detail Level:",
                options=["Concise", "Moderate", "Detailed"]
            )
        with col2:
            st.markdown("### Content Control")
            content_filters = st.multiselect(
                "Enable Content Filters:",
                ["Fact Verification", "Bias Detection", "Civility Check"],
                default=["Civility Check"]
            )
            real_time_updates = st.checkbox("Show Real-time Agent Thinking", value=False)

    if st.button("Start Debate"):
        if topic:
            with st.spinner("Initializing debate..."):
                try:
                    llm = HFInferenceLLM(api_token)

                    # Update parameters with advanced settings
                    parameters.update({
                        'agent_strategy': agent_strategy,
                        'response_length': response_length,
                        'content_filters': content_filters,
                        'real_time_updates': real_time_updates
                    })
                    
                    debate = DebateSystem(topic, llm, parameters)
                    
                    if parameters['show_thinking']:
                        st.sidebar.markdown("### Debate Progress")
                        progress_bar = st.sidebar.progress(0)
                    
                    debate_log = debate.run_debate_round()
                    
                    # Display debate with improved formatting
                    for index, event in enumerate(debate_log):
                        # Update progress if enabled
                        if parameters['show_thinking']:
                            progress = (index + 1) / len(debate_log)
                            progress_bar.progress(progress)
                        
                        # Display event based on type
                        if event['type'] == "MODERATOR":
                            st.write("🎙️ **Moderator:**")
                            st.markdown(event['content'])
                        elif "REBUTTAL" in event['type']:
                            st.write(f"🔄 **{event['type'].replace('_REBUTTAL', '')} Rebuttal:**")
                            st.markdown(event['content'])
                        elif "CLOSING" in event['type']:
                            st.write(f"🎭 **{event['type'].replace('_CLOSING', '')} Closing:**")
                            st.markdown(event['content'])
                        elif event['type'] in ["PROPONENT", "OPPONENT"]:
                            st.write(f"🗣️ **{event['type']}:**")
                            st.markdown(event['content'])
                        elif event['type'] == "FACT_CHECK":
                            with st.expander("📋 Fact Check"):
                                st.markdown(event['content'])
                        
                        # Add separator between events
                        st.markdown("---")

                    
                    if debate_log:  # Check if we have any debate content
                        st.sidebar.markdown("### Debate Statistics")
                        stats = {
                            "Total Exchanges": len(debate_log),
                            "Pro Arguments": len([e for e in debate_log if "PROPONENT" in e['type']]),
                            "Con Arguments": len([e for e in debate_log if "OPPONENT" in e['type']]),
                            "Fact Checks": len([e for e in debate_log if e['type'] == "FACT_CHECK"])
                        }
                        st.sidebar.json(stats)
                        
                        # Add download button
                        transcript = "\n\n".join([
                            f"{event['type']}: {event['content']}" 
                            for event in debate_log
                        ])
                        
                        st.download_button(
                            label="Download Debate Transcript",
                            data=transcript,
                            file_name="debate_transcript.txt",
                            mime="text/plain"
                        )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a debate topic")

if __name__ == "__main__":
    main()
# test streamlit run src/main.py
