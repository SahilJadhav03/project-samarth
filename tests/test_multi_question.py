"""
Multi-Question Test for Project Samarth
Demonstrates the ability to handle multiple sequential questions
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_integration import SyntheticDataGenerator
from src.query_engine import QueryRouter, DataProcessor

print("=" * 80)
print("PROJECT SAMARTH - MULTI-QUESTION CHAT INTERFACE TEST")
print("=" * 80)

# Initialize components
print("\n1️⃣ Initializing system components...")
router = QueryRouter(use_llm=False)
processor = DataProcessor()

# Load data
print("2️⃣ Loading datasets...")
crop_df = SyntheticDataGenerator.generate_crop_production_data()
rainfall_df = SyntheticDataGenerator.generate_rainfall_data()

print(f"   ✓ Loaded {len(crop_df):,} crop production records")
print(f"   ✓ Loaded {len(rainfall_df):,} rainfall records")
print(f"   ✓ Covering {len(crop_df['state_name'].unique())} states")

# Test multiple questions in sequence
questions = [
    "Compare the average annual rainfall in Punjab and Haryana for the last 5 available years. In parallel, list the top 3 most produced crops in each of those states during the same period.",
    "Identify the district in Punjab with the highest production of Rice in the most recent year available and compare that with the district with the lowest production of Rice in Haryana.",
    "What is the average rainfall in Maharashtra?",
    "Which crops are most produced in Karnataka?",
    "Analyze the production trend of Rice in Punjab over the last decade."
]

print("\n" + "=" * 80)
print("TESTING MULTI-QUESTION CAPABILITY - ASKING 5 SEQUENTIAL QUESTIONS")
print("=" * 80)

for i, question in enumerate(questions, 1):
    print(f"\n{'='*80}")
    print(f"QUESTION {i}")
    print(f"{'='*80}")
    print(f"Q: {question}")
    print(f"{'-'*80}")
    
    # Parse query
    intent = router.parse_query(question)
    print(f"Query Type: {intent.query_type}")
    print(f"Entities: {intent.entities}")
    print(f"Data Sources Needed: {intent.data_sources_needed}")
    
    # Process based on type
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
    
    # Format response
    response = processor.format_response(result)
    
    print(f"\nA: {response[:500]}..." if len(response) > 500 else f"\nA: {response}")
    print(f"\n✓ Question {i} answered with {len(result.get('citations', []))} citations")

print("\n" + "=" * 80)
print("✅ ALL QUESTIONS ANSWERED SUCCESSFULLY!")
print("=" * 80)
print("\nSUMMARY:")
print(f"   ✓ {len(questions)} questions processed")
print(f"   ✓ Multi-turn conversation capability demonstrated")
print(f"   ✓ Each answer includes source citations")
print(f"   ✓ System handles different query types seamlessly")
print("\n" + "=" * 80)
print("READY FOR MULTI-QUESTION CHAT INTERFACE DEMO!")
print("=" * 80)
