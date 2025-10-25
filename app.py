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
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
            <h1 style='color: white; margin: 0; font-size: 2rem;'>🌾 Samarth</h1>
            <p style='color: #E8F5E9; margin: 5px 0 0 0; font-size: 0.9rem;'>Agricultural Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
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
    
    # Sample questions as clickable buttons
    st.markdown("### 📝 Sample Questions")
    st.markdown("*Click any question below to auto-fill it in the chat box:*")
    
    sample_questions = [
        "Compare the average annual rainfall in Punjab and Haryana for the last 5 available years. In parallel, list the top 3 most produced crops in each of those states during the same period.",
        "Identify the district in Punjab with the highest production of Rice in the most recent year available and compare that with the district with the lowest production of Rice in Haryana.",
        "Analyze the production trend of Rice in Punjab over the last decade. Correlate this trend with the corresponding climate data for the same period.",
        "A policy advisor is proposing a scheme to promote drought-resistant crops over water-intensive crops in Maharashtra. Based on historical data from the last 5 years, what are the three most compelling data-backed arguments to support this policy?",
        "What is the average Wheat production in Karnataka over the last 3 years?",
        "Which state has the highest Sugarcane production?",
        "How does rainfall in Maharashtra correlate with Cotton production?"
    ]
    
    # Initialize selected_question if not exists
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = ''
    
    # Display sample questions as clickable buttons
    for idx, question in enumerate(sample_questions, 1):
        col1, col2 = st.columns([0.95, 0.05])
        with col1:
            if st.button(f"Q{idx}. {question[:80]}{'...' if len(question) > 80 else ''}", key=f"sample_{idx}", use_container_width=True):
                st.session_state.selected_question = question
                st.rerun()
        with col2:
            st.markdown("🔽" if len(question) > 80 else "")
    
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
    else:
        # Friendly welcome message
        st.markdown("### 👋 Welcome to Project Samarth!")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); padding: 25px; border-radius: 10px; border-left: 5px solid #4CAF50;'>
            <h4 style='color: #2E7D32; margin-top: 0;'>Hi there! I'm here to help you explore India's agricultural and climate data from data.gov.in. 👋</h4>
            <p style='color: #1B5E20; margin-bottom: 15px;'><strong>How I can assist you:</strong></p>
            <ul style='color: #2E7D32;'>
                <li>🌾 <strong>Compare crop production</strong> across states and districts</li>
                <li>🌧️ <strong>Analyze rainfall patterns</strong> and trends over time</li>
                <li>📊 <strong>Understand correlations</strong> between weather and agriculture</li>
                <li>📋 <strong>Generate data-backed policy recommendations</strong></li>
            </ul>
            <p style='color: #1B5E20; margin-bottom: 0;'><strong>✨ Get started:</strong> Click any sample question above, or type your own question below!</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")  # Add spacing
    
    # Query input section
    st.markdown("### 💬 Ask Your Question")
    
    # Initialize query_text in session state if not exists
    if 'query_text' not in st.session_state:
        st.session_state.query_text = ''
    
    # If a sample question was selected, update query_text
    if st.session_state.selected_question:
        st.session_state.query_text = st.session_state.selected_question
        st.session_state.selected_question = ''
    
    query = st.text_area(
        "Type your question here, or click a sample question above to get started:",
        value=st.session_state.query_text,
        height=100,
        placeholder="💡 Example: Compare rainfall in Punjab and Haryana over the last 5 years, and show top 3 crops..."
    )
    
    # Update session state with current query value
    st.session_state.query_text = query
    
    col1, col2 = st.columns([3, 1])
    with col1:
        submit_button = st.button("🔍 Ask Question", type="primary", width="stretch")
    with col2:
        show_raw = st.checkbox("Show Raw Data", value=False)
    
    # Process button
    if submit_button and query:
        with st.spinner("🤔 Let me find that information for you..."):
            try:
                # Increment query count
                st.session_state.query_count += 1
                
                # Add user message to chat
                st.session_state.messages.append({
                    "role": "user",
                    "content": query,
                    "number": st.session_state.query_count
                })
                
                # Add a friendly greeting for first question
                greeting = ""
                if st.session_state.query_count == 1:
                    greeting = "**Hi! I'd love to help you with that.** 😊 Let me analyze the data for you...\n\n---\n\n"
                
                # Process query
                response, result = process_query(query, router, processor, crop_df, rainfall_df)
                
                # Add friendly tone to response
                friendly_response = greeting + response + "\n\n---\n\n*Hope this helps! Feel free to ask more questions anytime.* �"
                
                # Add assistant response to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": friendly_response,
                    "raw_data": result,
                    "show_raw": show_raw
                })
                
                # Success message
                st.success(f"✅ Got it! Question {st.session_state.query_count} answered with citations. What would you like to explore next?")
                
                # Clear the input for next question
                st.session_state.query_text = ''
                
                # Rerun to update chat display and clear input
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Oops! I encountered an error: {str(e)}. Could you try rephrasing your question?")
                logger.error(f"Error: {e}", exc_info=True)
    elif submit_button:
        st.warning("⚠️ Please enter a question so I can help you analyze the data.")
    
    # Quick actions - only show after first question
    if st.session_state.messages:
        st.markdown("---")
        st.markdown("### 🎯 Quick Actions")
        st.markdown("*Click a button to auto-fill a question:*")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 Ask About Different State", key="quick_state"):
                st.session_state.selected_question = "Compare crop production in Tamil Nadu and Kerala"
                st.rerun()
        with col2:
            if st.button("🌧️ Ask About Rainfall", key="quick_rain"):
                st.session_state.selected_question = "What is the rainfall trend in Rajasthan over the last 5 years?"
                st.rerun()
        with col3:
            if st.button("📈 Ask About Trends", key="quick_trend"):
                st.session_state.selected_question = "Show me production trends for Cotton in Gujarat"
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
