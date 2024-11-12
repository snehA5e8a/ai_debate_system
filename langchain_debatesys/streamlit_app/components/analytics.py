import streamlit as st
import numpy as np
from typing import Dict

def render_analytics(analytics: Dict):
    """Render debate analytics with visualizations"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Debate Duration",
            value=f"{analytics['duration'] / 60:.1f} min"
        )
        st.metric(
            label="Interventions",
            value=analytics['interventions']
        )
    
    with col2:
        st.metric(
            label="Topic Adherence",
            value=f"{analytics['topic_adherence']:.1%}"
        )
        st.metric(
            label="Content Violations",
            value=analytics.get('violations', 0)
        )
    
    # Speaker Times Chart
    st.subheader("Speaking Time Distribution")
    speaker_times = analytics.get('speaker_times', {})
    if speaker_times:
        times = list(speaker_times.values())
        speakers = list(speaker_times.keys())
        
        # Create a bar chart
        st.bar_chart(
            {"Speaking Time (min)": [t/60 for t in times]},
            y="Speaking Time (min)"
        )
        
    # Topic Adherence Timeline
    if 'topic_adherence_timeline' in analytics:
        st.subheader("Topic Adherence Over Time")
        st.line_chart(analytics['topic_adherence_timeline'])