"""
Test script for Project Samarth
Tests all components with sample questions
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_integration import DataGovIntegrator, SyntheticDataGenerator
from src.query_engine import QueryRouter, DataProcessor
from src import config

def test_system():
    """Test the complete system with sample questions"""
    
    print("=" * 80)
    print("PROJECT SAMARTH - SYSTEM TEST")
    print("=" * 80)
    print()
    
    # Initialize components
    print("✓ Initializing system components...")
    integrator = DataGovIntegrator(
        api_key=config.DATA_GOV_API_KEY,
        cache_dir=config.CACHE_DIR
    )
    router = QueryRouter()
    processor = DataProcessor()
    
    # Load data (using synthetic for demo)
    print("✓ Loading datasets...")
    crop_df = SyntheticDataGenerator.generate_crop_production_data()
    rainfall_df = SyntheticDataGenerator.generate_rainfall_data()
    
    print(f"  - Crop production records: {len(crop_df)}")
    print(f"  - Rainfall records: {len(rainfall_df)}")
    print(f"  - States covered: {len(crop_df['state_name'].unique())}")
    print()
    
    # Sample questions
    sample_questions = [
        "Compare the average annual rainfall in Punjab and Haryana for the last 5 available years. In parallel, list the top 3 most produced crops in each of those states during the same period.",
        
        "Identify the district in Punjab with the highest production of Rice in the most recent year available and compare that with the district with the lowest production of Rice in Haryana.",
        
        "Analyze the production trend of Rice in Punjab over the last decade. Correlate this trend with the corresponding climate data for the same period.",
        
        "A policy advisor is proposing a scheme to promote drought-resistant crops over water-intensive crops in Maharashtra. Based on historical data from the last 5 years, what are the three most compelling data-backed arguments to support this policy?"
    ]
    
    # Test each question
    for i, question in enumerate(sample_questions, 1):
        print("=" * 80)
        print(f"SAMPLE QUESTION {i}")
        print("=" * 80)
        print(f"Q: {question}")
        print()
        
        # Parse query
        intent = router.parse_query(question)
        print(f"✓ Query Type: {intent.query_type}")
        print(f"✓ Entities Found: {intent.entities}")
        print(f"✓ Data Sources: {intent.data_sources_needed}")
        print()
        
        # Process query
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
            result = processor.process_production_query(crop_df, rainfall_df, intent)
        
        # Format and display response
        response = processor.format_response(result)
        print("ANSWER:")
        print("-" * 80)
        print(response)
        print()
        print(f"✓ Citations: {len(result.get('citations', []))} data sources cited")
        print()
    
    print("=" * 80)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print("Next step: Run the web interface with:")
    print('  "C:\\Users\\hp\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m streamlit run app.py')
    print()


if __name__ == "__main__":
    test_system()
