"""
Streamlit Web Interface for Project Samarth
Intelligent Q&A System over data.gov.in datasets
"""

import streamlit as st
import pandas as pd
from src.data_integration import DataGovIntegrator, SyntheticDataGenerator
from src.query_engine import QueryRouter, DataProcessor
from src import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Project Samarth - Agricultural Q&A System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-size: 1rem;
    }
    .citation-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #f1f8e9;
        border-left: 4px solid #2E7D32;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize the data integration and query processing system"""
    
    # Initialize data integrator
    integrator = DataGovIntegrator(
        api_key=config.DATA_GOV_API_KEY,
        cache_dir=config.CACHE_DIR
    )
    
    # Initialize query router and processor
    router = QueryRouter(use_llm=False)
    processor = DataProcessor()
    
    return integrator, router, processor


@st.cache_data
def load_datasets(_integrator, use_synthetic=False):
    """Load datasets from data.gov.in or use synthetic data"""
    
    if use_synthetic:
        st.info("🔄 Using synthetic data for demonstration purposes")
        crop_df = SyntheticDataGenerator.generate_crop_production_data()
        rainfall_df = SyntheticDataGenerator.generate_rainfall_data()
    else:
        try:
            # Try to fetch from data.gov.in
            with st.spinner("Fetching data from data.gov.in..."):
                crop_df = _integrator.fetch_crop_production()
                rainfall_df = _integrator.fetch_rainfall_data()
            
            # If empty, fall back to synthetic
            if crop_df.empty or rainfall_df.empty:
                st.warning("⚠️ Unable to fetch from data.gov.in API. Using synthetic data.")
                crop_df = SyntheticDataGenerator.generate_crop_production_data()
                rainfall_df = SyntheticDataGenerator.generate_rainfall_data()
        except Exception as e:
            st.warning(f"⚠️ Error accessing data.gov.in: {str(e)}. Using synthetic data.")
            crop_df = SyntheticDataGenerator.generate_crop_production_data()
            rainfall_df = SyntheticDataGenerator.generate_rainfall_data()
    
    return crop_df, rainfall_df


def process_query(query: str, router, processor, crop_df, rainfall_df):
    """Process user query and generate response"""
    
    # Parse query intent
    intent = router.parse_query(query)
    
    # Process based on query type
    if intent.query_type == "rainfall_comparison":
        result = processor.process_rainfall_comparison(rainfall_df, crop_df, intent)
    elif intent.query_type == "rainfall_query":
        result = processor.process_rainfall_query(rainfall_df, intent)
    elif intent.query_type == "district_ranking":
        result = processor.process_district_ranking(crop_df, intent)
    elif intent.query_type == "state_ranking":
        result = processor.process_state_ranking(crop_df, intent)
    elif intent.query_type == "trend_analysis":
        result = processor.process_trend_analysis(crop_df, rainfall_df, intent)
    elif intent.query_type == "policy_support":
        result = processor.process_policy_support(crop_df, rainfall_df, intent)
    elif intent.query_type == "production_query":
        result = processor.process_production_query(crop_df, rainfall_df, intent)
    elif intent.query_type == "production_comparison":
        result = processor.process_production_comparison(crop_df, intent)
    elif intent.query_type == "correlation_query":
        result = processor.process_correlation_query(crop_df, rainfall_df, intent)
    elif intent.query_type == "clarification":
        result = processor.process_clarification_query(intent)
    else:
        # Default to production query
        result = processor.process_production_query(crop_df, rainfall_df, intent)
    
    # Format response
    response = processor.format_response(result)
    
    return response, result


def main():
    """Main application"""
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0
    
    # Header
    st.markdown('<h1 class="main-header">🌾 Project Samarth</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligent Multi-Turn Q&A Chat System for Agricultural & Climate Data</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/2E7D32/FFFFFF?text=Project+Samarth", width="stretch")
        
        st.markdown("---")
        st.markdown("### About")
        st.info("""
        This system integrates data from **data.gov.in** to answer complex questions about:
        - 🌾 Agricultural production
        - 🌧️ Climate patterns
        - 📊 Cross-domain insights
        
        **Chat Interface:** Ask multiple questions in sequence!
        """)
        
        st.markdown("---")
        st.markdown("### Data Sources")
        st.markdown("""
        - Ministry of Agriculture & Farmers Welfare
        - India Meteorological Department (IMD)
        - District-wise Crop Production Statistics
        """)
        
        st.markdown("---")
        use_synthetic = st.checkbox("Use Synthetic Demo Data", value=True, 
                                    help="Enable this for faster demo without API calls")
        
        st.markdown("---")
        
        # Chat history management
        st.markdown("### 💬 Conversation")
        st.metric("Questions Asked", st.session_state.query_count)
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.query_count = 0
            st.rerun()
        
        st.markdown("---")
        st.markdown("### System Design")
        st.markdown("""
        **Architecture:**
        1. Data Integration Layer
        2. Query Router (Pattern/LLM)
        3. Multi-source Synthesis
        4. Citation Engine
        5. **Multi-turn Chat**
        """)
    
    # Initialize system
    integrator, router, processor = initialize_system()
    
    # Load datasets
    crop_df, rainfall_df = load_datasets(integrator, use_synthetic=use_synthetic)
    
    # Display dataset info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Crop Records", f"{len(crop_df):,}")
    with col2:
        st.metric("Rainfall Records", f"{len(rainfall_df):,}")
    with col3:
        st.metric("States Covered", len(crop_df["state_name"].unique()) if not crop_df.empty else 0)
    
    st.markdown("---")
    
    # Sample questions
    st.markdown("### 📝 Sample Questions (Try asking multiple!)")
    
    sample_questions = [
        "Compare the average annual rainfall in Punjab and Haryana for the last 5 available years. In parallel, list the top 3 most produced crops in each of those states during the same period.",
        "Identify the district in Punjab with the highest production of Rice in the most recent year available and compare that with the district with the lowest production of Rice in Haryana.",
        "Analyze the production trend of Rice in Punjab over the last decade. Correlate this trend with the corresponding climate data for the same period.",
        "A policy advisor is proposing a scheme to promote drought-resistant crops over water-intensive crops in Maharashtra. Based on historical data from the last 5 years, what are the three most compelling data-backed arguments to support this policy?",
        "What is the average Wheat production in Karnataka over the last 3 years?",
        "Which state has the highest Sugarcane production?",
        "How does rainfall in Maharashtra correlate with Cotton production?"
    ]
    
    # Display all sample questions in a list
    for idx, question in enumerate(sample_questions, 1):
        st.markdown(f"**Q{idx}.** {question}")
    
    st.markdown("---")
    
    # Display chat history
    if st.session_state.messages:
        st.markdown("### 💬 Chat History")
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(f"**Question {msg.get('number', i+1)}:** {msg['content']}")
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg['content'])
                    if msg.get('show_raw'):
                        with st.expander("🔍 View Raw Data"):
                            st.json(msg.get('raw_data', {}))
        
        st.markdown("---")
    
    # Query input
    st.markdown("### 💬 Ask Your Question")
    
    # Initialize input value in session state
    if 'input_value' not in st.session_state:
        st.session_state.input_value = ''
    
    # Check if a sample question was clicked
    if 'current_question' in st.session_state:
        st.session_state.input_value = st.session_state.pop('current_question')
    
    query = st.text_area(
        "Enter your question about agricultural and climate data:",
        value=st.session_state.input_value,
        height=100,
        key="query_input",
        placeholder="E.g., Compare rainfall in Punjab and Haryana over the last 5 years..."
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        submit_button = st.button("🔍 Ask Question", type="primary", width="stretch")
    with col2:
        show_raw = st.checkbox("Show Raw Data", value=False)
    
    # Process button
    if submit_button:
        if query:
            with st.spinner("🤔 Processing your query..."):
                try:
                    # Increment query count
                    st.session_state.query_count += 1
                    
                    # Add user message to chat
                    st.session_state.messages.append({
                        "role": "user",
                        "content": query,
                        "number": st.session_state.query_count
                    })
                    
                    # Process query
                    response, result = process_query(query, router, processor, crop_df, rainfall_df)
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "raw_data": result,
                        "show_raw": show_raw
                    })
                    
                    # Success message
                    st.success(f"✅ Question {st.session_state.query_count} answered! All data points are cited with sources.")
                    
                    # Clear the input box for next question
                    st.session_state.input_value = ''
                    
                    # Rerun to update chat display and clear input
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error processing query: {str(e)}")
                    logger.error(f"Error: {e}", exc_info=True)
        else:
            st.warning("⚠️ Please enter a question to analyze.")
    
    # Quick actions
    if st.session_state.messages:
        st.markdown("---")
        st.markdown("### 🎯 Quick Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 Ask About Different State"):
                st.session_state.current_question = "Compare crop production in Tamil Nadu and Kerala"
                st.rerun()
        with col2:
            if st.button("🌧️ Ask About Rainfall"):
                st.session_state.current_question = "What is the rainfall trend in Rajasthan over the last 5 years?"
                st.rerun()
        with col3:
            if st.button("📈 Ask About Trends"):
                st.session_state.current_question = "Show me production trends for Cotton in Gujarat"
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888;'>
        <p>Project Samarth | Data Sovereignty • Accuracy • Traceability • Multi-Turn Chat</p>
        <p style='font-size: 0.8rem;'>All data sourced from data.gov.in | Built for end-to-end intelligent Q&A</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
