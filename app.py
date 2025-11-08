import os
import tempfile
import streamlit as st
from PIL import Image
import io
import base64
from typing import Optional

from integrated_system import AILearningPlatform
from config import Config

# Page configuration
st.set_page_config(
    page_title="Community Issue Analyzer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'platform' not in st.session_state:
    try:
        st.session_state.platform = AILearningPlatform()
        st.session_state.api_configured = True
    except ValueError as e:
        st.session_state.api_configured = False
        st.session_state.error_message = str(e)

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None


def display_header():
    """Display the application header"""
    st.markdown('<div class="main-header">AI-Powered Learning Platform</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Recognize and translate community challenges into structured learning missions statements</div>',
        unsafe_allow_html=True
    )


def process_image(image_file, domains):
    """Process uploaded image"""
    with st.spinner("Analyzing image..."):
        # Save uploaded file temporarily
        image = Image.open(image_file)
        
        # Convert to bytes for processing
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format or 'PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Save temporarily
        temp_path = "/tmp/uploaded_image.jpg"
        with open(temp_path, "wb") as f:
            f.write(img_byte_arr)
        
        # Process with platform
        result = st.session_state.platform.process_image(temp_path, domains=domains)
        
        return result


def process_text(problem_description):
    """Process text description"""
    with st.spinner("Processing description..."):
        result = st.session_state.platform.process_text_description(problem_description)
        return result


def display_results(result):
    """Display analysis results"""
    if not result.get('success'):
        st.error(f"Error: {result.get('error', 'Unknown error occurred')}")
        return
    
    st.success("Analysis Complete!")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Detection", "Classification", "Mission Statement"])

    with tab1:
        st.markdown("### Vision Analysis" if 'vision_analysis' in result else "### Problem Description")
        
        if 'vision_analysis' in result:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(result['vision_analysis'])
            st.markdown('</div>', unsafe_allow_html=True)
        elif 'original_description' in result:
            st.info(f"**Original Description:** {result['original_description']}")
    
    with tab2:
        st.markdown("### Problem Classification")
        
        classification = result.get('classification', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            category = classification.get('category', 'Unknown')
            emoji_map = {
                'Environment': '',
                'Health': '',
                'Education': ''
            }
            st.metric("Category", f"{emoji_map.get(category, '❓')} {category}")
        
        with col2:
            confidence = classification.get('confidence', 'Unknown')
            st.metric("Confidence", confidence)
        
        if classification.get('reasoning'):
            st.markdown("**Reasoning:**")
            st.info(classification['reasoning'])
    
    with tab3:
        st.markdown("### Mission Statement")
        
        mission = result.get('mission_statement', {})
        
        if mission.get('mission_statement'):
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown(f"**{mission['mission_statement']}**")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Problem Definition
        if mission.get('problem_definition'):
            st.markdown("#### Problem Definition")
            st.write(mission['problem_definition'])
        
        # Goal
        if mission.get('goal'):
            st.markdown("#### Goal")
            st.write(mission['goal'])
        
        # Expected Impact
        if mission.get('expected_impact'):
            st.markdown("#### Expected Impact")
            st.write(mission['expected_impact'])
        
        # Action Steps
        if mission.get('action_steps'):
            st.markdown("#### Action Steps")
            for i, step in enumerate(mission['action_steps'], 1):
                st.markdown(f"{i}. {step}")
    
    # Download results
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        # Create download content
        download_content = f"""
# Community Issue Analysis Report

## Classification
- **Category**: {result.get('classification', {}).get('category', 'N/A')}
- **Confidence**: {result.get('classification', {}).get('confidence', 'N/A')}

## Mission Statement
{result.get('mission_statement', {}).get('mission_statement', 'N/A')}

## Problem Definition
{result.get('mission_statement', {}).get('problem_definition', 'N/A')}

## Goal
{result.get('mission_statement', {}).get('goal', 'N/A')}

## Expected Impact
{result.get('mission_statement', {}).get('expected_impact', 'N/A')}

## Action Steps
"""
        for i, step in enumerate(result.get('mission_statement', {}).get('action_steps', []), 1):
            download_content += f"{i}. {step}\n"
        
        st.download_button(
            label="Download Report",
            data=download_content,
            file_name="community_issue_report.txt",
            mime="text/plain"
        )


def main():
    """Main application"""
    # Display header
    display_header()
    
    # Check API configuration
    if not st.session_state.api_configured:
        st.error("Gemini API key not configured!")
        st.markdown("""
        Please set your Gemini API key in the `.env` file:
        ```
        GEMINI_API_KEY=your_api_key_here
        ```
        Then restart the application.
        """)
        return
    
    # Main content area
    st.markdown("---")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Upload Image", "Describe Problem"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if input_method == "Upload Image":
        # Image upload section
        st.markdown("### Upload Community Issue Image")
        st.markdown("Upload a photo showing a community problem (environment, health, or education issue)")
        
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
            help="Supported formats: PNG, JPG, JPEG, GIF, WEBP"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if uploaded_file is not None:
                # Display uploaded image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_container_width=True)
        
        # Analyze button
        if uploaded_file is not None:
            if st.button("Analyze Image", key="analyze_image"):
                domains = st.session_state.get('selected_domains', Config.CATEGORIES)
                result = process_image(uploaded_file, domains)
                st.session_state.analysis_result = result
    
    else:  # Text description
        # Text input section
        st.markdown("### Describe the Community Problem")
        st.markdown("Write a brief description of the community issue you want to address")
        
        problem_description = st.text_area(
            "Problem Description:",
            placeholder="Example: Our street is always flooded when it rains...",
            height=150,
            help="Describe the community problem in your own words"
        )
        
        # Analyze button
        if problem_description:
            if st.button("Analyze Description", key="analyze_text"):
                result = process_text(problem_description)
                st.session_state.analysis_result = result
    
    # Display results if available
    if st.session_state.analysis_result:
        st.markdown("---")
        st.markdown("## Analysis Results")
        display_results(st.session_state.analysis_result)

if __name__ == "__main__":
    main()
