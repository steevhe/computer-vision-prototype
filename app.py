import streamlit as st
from PIL import Image
import io
import base64
from typing import Optional

from integrated_system import AILearningPlatform
from ai_mentor import AIMentor
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

if 'mentor' not in st.session_state:
    try:
        st.session_state.mentor = AIMentor()
    except ValueError:
        st.session_state.mentor = None

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

if 'mentor_conversation' not in st.session_state:
    st.session_state.mentor_conversation = []


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


def display_mentor_interface():
    """Display AI Mentor interface with two modes"""
    st.markdown("### AI Mentor & Guidance System")
    st.markdown("Get personalized guidance through critical thinking or solution templates")
    
    # Mode selection
    mentor_mode = st.radio(
        "Select Mentor Mode:",
        ["Critical Thinking Mode", "Solution Mode", "Interactive Chat"],
        horizontal=True,
        help="Critical Thinking: Socratic questions | Solution: Quick templates | Chat: Conversational guidance"
    )
    
    st.markdown("---")
    
    if mentor_mode == "Critical Thinking Mode":
        display_critical_thinking_mode()
    elif mentor_mode == "Solution Mode":
        display_solution_mode()
    else:
        display_interactive_chat()


def display_critical_thinking_mode():
    """Display Critical Thinking Mode interface"""
    st.markdown("#### Critical Thinking Mode")
    st.info("Explore your problem through Socratic questioning. The mentor will guide you with thought-provoking questions.")
    
    problem_input = st.text_area(
        "Describe the problem or topic you want to explore:",
        placeholder="Example: How can we reduce plastic waste in our community?",
        height=150,
        key="ct_problem"
    )
    
    if st.button("Get Socratic Guidance", key="ct_button"):
        if problem_input:
            with st.spinner("Generating thought-provoking questions..."):
                result = st.session_state.mentor.critical_thinking_mode(
                    problem_input,
                    None
                )
                
                if result.get('success'):
                    st.success("Guidance Generated!")
                    
                    # Display guiding questions
                    if result.get('guiding_questions'):
                        st.markdown("##### Guiding Questions")
                        st.markdown('<div class="info-box">', unsafe_allow_html=True)
                        for i, question in enumerate(result['guiding_questions'], 1):
                            st.markdown(f"**{i}.** {question}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display reflection prompts
                    if result.get('reflection_prompts'):
                        st.markdown("##### Reflection Prompts")
                        for prompt in result['reflection_prompts']:
                            st.info(prompt)
                    
                    # Display challenge points
                    if result.get('challenge_points'):
                        st.markdown("##### Challenge Points")
                        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                        for point in result['challenge_points']:
                            st.markdown(f"- {point}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display next steps
                    if result.get('next_steps'):
                        st.markdown("##### Suggested Next Steps")
                        for step in result['next_steps']:
                            st.markdown(f"- {step}")
                else:
                    st.error(f"Error: {result.get('error')}")
        else:
            st.warning("Please describe a problem or topic first.")


def display_solution_mode():
    """Display Solution Mode interface with templates"""
    st.markdown("#### Solution Mode")
    st.info("Get practical frameworks and templates to structure your approach.")
    
    problem_input = st.text_area(
        "Describe the problem you want to solve:",
        placeholder="Example: We need to improve literacy rates in our community...",
        height=120,
        key="sol_problem"
    )
    
    template_type = st.selectbox(
        "Select Template Type:",
        ["Auto-detect", "SWOT Analysis", "Budget Outline", "Action Plan", 
         "Stakeholder Analysis", "Project Timeline"],
        help="Auto-detect will choose the best template for your problem"
    )
    
    if st.button("Generate Template", key="sol_button"):
        if problem_input:
            with st.spinner("Creating solution template..."):
                # Map selections
                template_map = {
                    "Auto-detect": "auto",
                    "SWOT Analysis": "swot",
                    "Budget Outline": "budget",
                    "Action Plan": "action_plan",
                    "Stakeholder Analysis": "stakeholder",
                    "Project Timeline": "timeline"
                }
                
                result = st.session_state.mentor.solution_mode(
                    problem_input,
                    template_map[template_type],
                    None
                )
                
                if result.get('success'):
                    st.success(f"Template Generated: {result.get('template_type', '').replace('_', ' ').title()}")
                    
                    # Display template
                    template_data = result.get('template', {})
                    if template_data:
                        st.markdown("##### Template")
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        
                        for section, items in template_data.items():
                            st.markdown(f"**{section}**")
                            if isinstance(items, list):
                                for item in items:
                                    st.markdown(f"- {item}")
                            else:
                                st.markdown(items)
                            st.markdown("")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display implementation guide
                    if result.get('implementation_guide'):
                        st.markdown("##### Implementation Guide")
                        st.info(result['implementation_guide'])
                    
                    # Display tips
                    if result.get('tips'):
                        st.markdown("##### Practical Tips")
                        for tip in result['tips']:
                            st.markdown(f"- {tip}")
                    
                    # Download button
                    download_content = f"""# {result.get('template_type', '').replace('_', ' ').title()} Template

Problem: {problem_input}

## Template

"""
                    for section, items in template_data.items():
                        download_content += f"\n### {section}\n"
                        if isinstance(items, list):
                            for item in items:
                                download_content += f"- {item}\n"
                        else:
                            download_content += f"{items}\n"
                    
                    if result.get('implementation_guide'):
                        download_content += f"\n## Implementation Guide\n{result['implementation_guide']}\n"
                    
                    if result.get('tips'):
                        download_content += "\n## Tips\n"
                        for tip in result['tips']:
                            download_content += f"- {tip}\n"
                    
                    st.download_button(
                        label="Download Template",
                        data=download_content,
                        file_name=f"{result.get('template_type', 'template')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(f"Error: {result.get('error')}")
        else:
            st.warning("Please describe a problem first.")


def display_interactive_chat():
    """Display interactive chat interface"""
    st.markdown("#### Interactive Mentor Chat")
    st.info("Have a conversation with the AI mentor. Choose your preferred guidance style.")
    
    chat_mode = st.radio(
        "Guidance Style:",
        ["Critical Thinking", "Solution-Focused"],
        horizontal=True,
        key="chat_mode_radio"
    )
    
    # Display conversation history
    if st.session_state.mentor_conversation:
        st.markdown("##### Conversation")
        for msg in st.session_state.mentor_conversation:
            if msg['role'] == 'user':
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**Mentor:** {msg['content']}")
            st.markdown("---")
    
    # Chat input
    user_message = st.text_area(
        "Your message:",
        placeholder="Ask a question or describe what you're thinking...",
        height=100,
        key="chat_input"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("Send", key="chat_send"):
            if user_message:
                mode = "critical_thinking" if chat_mode == "Critical Thinking" else "solution"
                
                with st.spinner("Mentor is thinking..."):
                    result = st.session_state.mentor.interactive_mentoring(user_message, mode)
                    
                    if result.get('success'):
                        st.session_state.mentor_conversation.append({
                            'role': 'user',
                            'content': user_message
                        })
                        st.session_state.mentor_conversation.append({
                            'role': 'mentor',
                            'content': result['mentor_response']
                        })
                        st.rerun()
                    else:
                        st.error(f"Error: {result.get('error')}")
            else:
                st.warning("Please enter a message.")
    
    with col2:
        if st.button("Clear Conversation", key="chat_clear"):
            st.session_state.mentor_conversation = []
            if st.session_state.mentor:
                st.session_state.mentor.reset_conversation()
            st.rerun()


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
    
    # Main navigation tabs
    main_tab1, main_tab2 = st.tabs(["Problem Analysis", "AI Mentor"])
    
    with main_tab1:
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
    
    with main_tab2:
        display_mentor_interface()

if __name__ == "__main__":
    main()
