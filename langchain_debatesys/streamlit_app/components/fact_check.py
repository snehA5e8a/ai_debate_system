import streamlit as st

def render_fact_check(check_result: dict):
    """Render fact checking results with colored indicators"""
    status_color = {
        'Highly Accurate': 'success',
        'Moderately Accurate': 'warning',
        'Low Accuracy': 'error',
        'Unverified': 'error'
    }
    
    st.markdown(
        f"""
        <div style='border: 1px solid; padding: 10px; border-radius: 5px;'>
        <h4>Fact Check Results</h4>
        <p>Overall Accuracy: <span class='{status_color.get(check_result["overall_accuracy"], "error")}'>{check_result["overall_accuracy"]}</span></p>
        <p>Confidence: {check_result["confidence"]:.2f}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with st.expander("Detailed Analysis"):
        for detail in check_result.get('details', []):
            st.markdown("---")
            st.write("**Claim:**", detail['claim'])
            st.write("**Status:**", detail['status'])
            st.write("**Confidence:**", f"{detail['confidence']:.2f}")
            st.write("**Reasoning:**", detail['reasoning'])
            if detail.get('corrections'):
                st.write("**Corrections:**", ", ".join(detail['corrections']))