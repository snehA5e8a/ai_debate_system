import streamlit as st
from typing import List, Dict

def render_debate_log(debate_log: List[Dict]):
    """Render the debate log with formatting and styling"""
    for entry in debate_log:
        # Style based on event type
        if entry['type'] == 'MODERATOR':
            st.markdown("### 👨‍⚖️ Moderator")
        elif 'PROPONENT' in entry['type']:
            st.markdown("### 🔵 Proponent")
        elif 'OPPONENT' in entry['type']:
            st.markdown("### 🔴 Opponent")
        elif entry['type'] == 'FACT_CHECK':
            st.markdown("### 🔍 Fact Check")
        
        # Display content
        st.markdown(entry['content'])
        
        # Show metadata if available
        if entry.get('metadata') and st.session_state.get('show_metadata', False):
            with st.expander("Metadata"):
                st.json(entry['metadata'])
        
        st.markdown("---")

def render_download_button(debate_log: List[Dict]):
    """Render download button for debate transcript"""
    transcript = "\n\n".join([
        f"{entry['type']}: {entry['content']}"
        for entry in debate_log
        if entry['type'] != 'ERROR'
    ])
    
    st.download_button(
        label="Download Debate Transcript",
        data=transcript,
        file_name="debate_transcript.txt",
        mime="text/plain"
    )