# main.py
import streamlit as st
import os
from dotenv import load_dotenv
from src.agents.llm import HFInferenceLLM
from src.agents.debate_agent import DebateAgent, DebateStyle
from src.agents.fact_checker import FactCheckerAgent
from src.agents.moderator import ModeratorAgent
import time
from typing import Dict, List

# Load environment variables
load_dotenv()

# Initialize Streamlit page config
st.set_page_config(
    page_title="Agentic AI Debate System",
    page_icon="🤖",
    layout="wide"
)

def render_agent_state(agent: DebateAgent, key: str):
    """Render agent's current state and metrics"""
    with st.container():
        st.subheader(f"{agent.name} State")
        
        # Display current state
        col1, col2 = st.columns(2)
        with col1:
            st.write("Current State:", agent.state.value)
            st.write("Emotional State:", agent.emotion.value)
        with col2:
            st.write("Personality Traits:")
            for trait, value in agent.personality.items():
                st.progress(value, text=f"{trait}: {value:.2f}")
        
        # Display active goals
        with st.expander("Active Goals"):
            for goal in agent.goals:
                if not goal.achieved:
                    st.progress(goal.progress, text=f"{goal.description}: {goal.progress:.0%}")

def render_fact_check(check_result: Dict):
    """Render fact checking results"""
    with st.container():
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
                st.write(f"Reason: {detail['reason']}")
                st.markdown("---")

def main():
    st.title("Agentic AI Debate System")
    
    # Sidebar for debate parameters
    st.sidebar.title("Debate Parameters")
    
    debate_style = st.sidebar.selectbox(
        "Debate Style:",
        [style.value for style in DebateStyle]
    )
    
    parameters = {
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
        'show_thinking': st.sidebar.checkbox(
            "Show Agent Thinking Process",
            value=True
        ),
        'real_time_fact_check': st.sidebar.checkbox(
            "Enable Real-time Fact Checking",
            value=True
        )
    }
    
    # Advanced Settings
    with st.sidebar.expander("Advanced Agent Settings"):
        agent_base_confidence = st.slider(
            "Agent Base Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.7
        )
        agent_adaptability = st.slider(
            "Agent Adaptability",
            min_value=0.0,
            max_value=1.0,
            value=0.5
        )
    
    # HuggingFace API setup
    api_token = st.text_input(
        "Enter your HuggingFace API token:",
        type="password",
        value=os.getenv('HUGGINGFACE_API_TOKEN', ''),
        help="Get your free token at https://huggingface.co/settings/tokens"
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
        # Initialize agents
        llm = HFInferenceLLM(api_token)
        proponent = DebateAgent(
            "Proponent", 
            "in favor", 
            llm, 
            DebateStyle(debate_style)
        )
        opponent = DebateAgent(
            "Opponent", 
            "against", 
            llm, 
            DebateStyle(debate_style)
        )
        fact_checker = FactCheckerAgent(llm)
        moderator = ModeratorAgent(llm)
        
        # Update agent personality traits
        for agent in [proponent, opponent]:
            agent.personality['confidence'] = agent_base_confidence
            agent.personality['adaptability'] = agent_adaptability
        
        # Set up columns for agent states
        if parameters['show_thinking']:
            col1, col2 = st.columns(2)
            with col1:
                render_agent_state(proponent, "proponent")
            with col2:
                render_agent_state(opponent, "opponent")
        
        # Run debate
        with st.spinner("Initializing debate..."):
            try:
                # Moderator introduction
                intro = moderator.moderate(topic, "introduction")
                st.markdown(f"**Moderator**: {intro['content']}")
                st.markdown("---")
                
                # Opening statements
                for agent, role in [(proponent, "Proponent"), (opponent, "Opponent")]:
                    statement = agent.generate_opening_statement(topic, parameters)
                    st.markdown(f"**{role}**: {statement['content']}")
                    
                    if parameters['real_time_fact_check']:
                        fact_check = fact_checker.check_statement(statement['content'])
                        render_fact_check(fact_check)
                    
                    if parameters['show_thinking']:
                        st.write(f"{role}'s Confidence:", statement['metadata']['confidence'])
                    
                    st.markdown("---")
                
                # Main debate rounds
                for round_num in range(parameters['debate_rounds']):
                    st.subheader(f"Round {round_num + 1}")
                    
                    for agent, role in [(proponent, "Proponent"), (opponent, "Opponent")]:
                        # Get last opponent statement
                        opponent_statement = opponent.arguments_made[-1].content if opponent.arguments_made else ""
                        
                        rebuttal = agent.generate_rebuttal(
                            topic,
                            opponent_statement,
                            parameters
                        )
                        
                        st.markdown(f"**{role}**: {rebuttal['content']}")
                        
                        if parameters['real_time_fact_check']:
                            fact_check = fact_checker.check_statement(rebuttal['content'])
                            render_fact_check(fact_check)
                        
                        if parameters['show_thinking']:
                            with st.expander(f"{role}'s Thinking Process"):
                                st.write("Points Addressed:", rebuttal['metadata']['points_addressed'])
                                st.write("Confidence:", rebuttal['metadata']['confidence'])
                        
                        st.markdown("---")
                        
                        # Moderator intervention if needed
                        intervention = moderator.moderate(topic, "intervention")
                        if intervention and intervention.get('content'):
                            st.markdown(f"**Moderator**: {intervention['content']}")
                            st.markdown("---")
                
                # Closing statements
                st.subheader("Closing Statements")
                for agent, role in [(proponent, "Proponent"), (opponent, "Opponent")]:
                    closing = agent.generate_closing_statement(topic, parameters)
                    st.markdown(f"**{role}**: {closing['content']}")
                    
                    if parameters['real_time_fact_check']:
                        fact_check = fact_checker.check_statement(closing['content'])
                        render_fact_check(fact_check)
                    
                    st.markdown("---")
                
                # Moderator closing
                closing = moderator.moderate(topic, "closing")
                st.markdown(f"**Moderator**: {closing['content']}")
                
                # Display debate analytics
                st.sidebar.markdown("### Debate Analytics")
                analytics = moderator.get_debate_analytics()
                st.sidebar.write("Duration:", f"{analytics['duration']:.1f}s")
                st.sidebar.write("Interventions:", analytics['interventions'])
                st.sidebar.write("Topic Adherence:", f"{analytics['topic_adherence']:.1%}")
                
                # Offer debate transcript download
                transcript = "\n\n".join([
                    f"{arg.type}: {arg.content}" 
                    for agent in [proponent, opponent] 
                    for arg in agent.arguments_made
                ])
                
                st.download_button(
                    label="Download Debate Transcript",
                    data=transcript,
                    file_name="debate_transcript.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"An error occurred during the debate: {str(e)}")

if __name__ == "__main__":
    main()