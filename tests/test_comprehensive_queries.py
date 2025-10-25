"""
Comprehensive Query Testing for Project Samarth
Tests 100+ different question variations to identify issues and improvements
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_integration import SyntheticDataGenerator
from src.query_engine import QueryRouter, DataProcessor
import json

# Test categories with variations
test_queries = {
    "Simple Production Queries": [
        "What is the wheat production in Punjab?",
        "Show me rice production in Haryana",
        "Cotton production in Maharashtra",
        "How much sugarcane is produced in Karnataka?",
        "Tell me about bajra production in Rajasthan",
        "What's the average wheat production in Punjab?",
        "Give me cotton production data for Maharashtra",
        "Show rice production statistics for Tamil Nadu",
        "What is jowar production in Karnataka?",
        "How much wheat is grown in Haryana?",
        "Production of rice in Punjab",
        "Sugarcane yield in Karnataka",
        "Cotton harvest in Maharashtra",
        "Wheat crop production in Haryana",
        "Rice farming output in Punjab",
    ],
    
    "Rainfall Queries": [
        "Punjab rainfall in 2023",
        "What is the rainfall in Maharashtra?",
        "Show me rain data for Haryana",
        "How much rain did Punjab get in 2022?",
        "Rainfall statistics for Karnataka",
        "Maharashtra precipitation in 2023",
        "Annual rainfall in Tamil Nadu",
        "Rain in Punjab",
        "Haryana monsoon data",
        "Karnataka rainfall trends",
        "What was the rainfall in Punjab last year?",
        "Show precipitation data for Maharashtra",
        "Rain statistics for Haryana in 2023",
        "How much precipitation in Karnataka?",
        "Punjab rain patterns",
    ],
    
    "Time-based Queries": [
        "Wheat production in Punjab over the last 3 years",
        "Rice production in Haryana from 2020 to 2023",
        "Cotton production trend in Maharashtra",
        "Punjab wheat production in the last decade",
        "5 year wheat production in Haryana",
        "Recent rice production in Punjab",
        "Historical cotton data for Maharashtra",
        "Wheat production between 2018 and 2022",
        "Last 5 years of sugarcane production in Karnataka",
        "Rice production over time in Tamil Nadu",
        "Decade-long wheat trends in Punjab",
        "Year-over-year cotton in Maharashtra",
        "Multi-year rice data for Haryana",
        "Production changes over 10 years in Punjab",
        "Long-term wheat trends",
    ],
    
    "Comparison Queries": [
        "Compare wheat production in Punjab and Haryana",
        "Punjab vs Haryana rice production",
        "Which state produces more cotton - Maharashtra or Karnataka?",
        "Rainfall comparison between Punjab and Haryana",
        "Compare sugarcane production in Karnataka and Tamil Nadu",
        "Punjab wheat vs Maharashtra cotton",
        "Haryana rice compared to Punjab rice",
        "Which has more rainfall - Punjab or Haryana?",
        "Production comparison across states",
        "Compare crop yields in Punjab and Haryana",
        "Maharashtra vs Karnataka cotton production",
        "Rainfall differences between states",
        "Cross-state production analysis",
        "Multi-state comparison of wheat",
        "State-wise rice production comparison",
    ],
    
    "Ranking/Extremes Queries": [
        "Which state has the highest wheat production?",
        "Lowest rice production state",
        "Top cotton producing state",
        "Which district in Punjab produces most rice?",
        "Highest rainfall state",
        "State with maximum sugarcane production",
        "Lowest rainfall region",
        "Best wheat producing district in Punjab",
        "Worst rice producing area in Haryana",
        "Top 3 cotton producing states",
        "Highest producing district",
        "Maximum rainfall location",
        "Peak wheat production state",
        "Minimum cotton production",
        "Leading rice producer",
    ],
    
    "Correlation Queries": [
        "How does rainfall affect wheat production in Punjab?",
        "Correlation between rain and rice in Haryana",
        "Does rainfall impact cotton production in Maharashtra?",
        "Relationship between precipitation and wheat yield",
        "Rain vs production in Punjab",
        "How rainfall correlates with crops",
        "Weather impact on wheat production",
        "Monsoon effect on rice in Tamil Nadu",
        "Precipitation and crop yield relationship",
        "Rainfall influence on sugarcane",
        "Climate correlation with production",
        "Does more rain mean more crops?",
        "Weather patterns and agriculture",
        "Rain dependency of wheat",
        "Moisture and crop output correlation",
    ],
    
    "Trend Analysis Queries": [
        "Analyze wheat production trend in Punjab",
        "Rice production trend over 10 years",
        "Is cotton production increasing in Maharashtra?",
        "Show me wheat trends in Haryana",
        "Production pattern analysis for Punjab",
        "Trend of sugarcane in Karnataka",
        "Historical rice production trends",
        "Is wheat production going up or down?",
        "Analyze crop production changes",
        "Long-term production patterns",
        "Wheat yield trends over time",
        "Cotton production trajectory",
        "Rice production growth or decline",
        "Temporal analysis of wheat",
        "Year-over-year production changes",
    ],
    
    "District-Level Queries": [
        "Which district in Punjab produces most wheat?",
        "Best rice producing district in Haryana",
        "District-wise cotton production in Maharashtra",
        "Top district for wheat in Punjab",
        "Lowest producing district in Haryana",
        "District comparison in Punjab",
        "Which area grows most rice?",
        "District-level wheat data",
        "Sub-state production analysis",
        "Regional wheat production",
        "District rankings for rice",
        "Local production statistics",
        "Area-wise crop data",
        "District production breakdown",
        "Regional agricultural output",
    ],
    
    "Average/Statistical Queries": [
        "Average wheat production in Punjab",
        "Mean rice production in Haryana",
        "Average rainfall in Maharashtra",
        "Mean annual wheat in Punjab",
        "What's the average cotton production?",
        "Mean precipitation in Karnataka",
        "Average crop yield in Punjab",
        "Statistical wheat data",
        "Mean rice output",
        "Average annual production",
        "Statistical analysis of wheat",
        "Mean crop production",
        "Average yield statistics",
        "Production averages",
        "Mean agricultural output",
    ],
    
    "Policy/Advisory Queries": [
        "Should we promote drought-resistant crops in Maharashtra?",
        "Policy recommendation for Punjab agriculture",
        "What crops are best for low rainfall areas?",
        "Agricultural advice for Haryana",
        "Crop recommendations based on rainfall",
        "Policy support for water-intensive crops",
        "Agricultural strategy for Maharashtra",
        "Drought-resistant vs water-intensive crops",
        "Data-backed policy arguments",
        "Agricultural planning recommendations",
        "Crop selection based on climate",
        "Policy insights from production data",
        "Strategic crop recommendations",
        "Evidence-based agricultural policy",
        "Crop planning advice",
    ],
    
    "Multi-part Complex Queries": [
        "Compare rainfall in Punjab and Haryana and list top 3 crops",
        "Show wheat production and rainfall correlation in Punjab",
        "Which state produces more rice and has higher rainfall?",
        "Analyze wheat trends and climate patterns in Punjab",
        "Production and rainfall comparison across states",
        "Multi-state production with weather data",
        "Combined crop and climate analysis",
        "Production trends with rainfall correlation",
        "Cross-domain agricultural insights",
        "Integrated production and weather analysis",
    ],
    
    "Vague/Ambiguous Queries": [
        "Tell me about Punjab",
        "What's happening in agriculture?",
        "Show me data",
        "Agriculture in India",
        "Crop information",
        "Weather data",
        "Production statistics",
        "Tell me about farming",
        "Agricultural data",
        "Crop yields",
        "Farming statistics",
        "Agricultural trends",
        "Crop production",
        "Rainfall data",
        "Agriculture statistics",
    ],
    
    "Negative/Edge Cases": [
        "What is the production of bananas in Punjab?",  # Crop not in dataset
        "Rainfall in Alaska",  # State not in dataset
        "Production in 1800",  # Year out of range
        "How many elephants in Punjab?",  # Nonsense query
        "What is the color of wheat?",  # Not a data query
        "Who is the farmer in Punjab?",  # Not answerable
        "Price of rice",  # Not in dataset
        "Export data for wheat",  # Not in dataset
        "Import statistics",  # Not in dataset
        "Market prices",  # Not in dataset
    ],
}

def run_comprehensive_test():
    """Run comprehensive testing"""
    
    print("=" * 100)
    print(" " * 30 + "COMPREHENSIVE QUERY TESTING")
    print("=" * 100)
    print()
    
    # Initialize system
    print("Initializing system components...")
    router = QueryRouter(use_llm=False)
    processor = DataProcessor()
    
    # Load data
    print("Loading datasets...")
    crop_df = SyntheticDataGenerator.generate_crop_production_data()
    rainfall_df = SyntheticDataGenerator.generate_rainfall_data()
    print(f"[OK] Loaded {len(crop_df)} crop records, {len(rainfall_df)} rainfall records")
    print()
    
    # Track results
    total_queries = 0
    successful = 0
    failed = 0
    results_by_category = {}
    issues_found = []
    
    # Test each category
    for category, queries in test_queries.items():
        print("=" * 100)
        print(f"CATEGORY: {category}")
        print("=" * 100)
        
        category_results = {
            "total": len(queries),
            "success": 0,
            "failed": 0,
            "issues": []
        }
        
        for idx, query in enumerate(queries, 1):
            total_queries += 1
            print(f"\n[{idx}/{len(queries)}] Query: {query}")
            
            try:
                # Parse query
                intent = router.parse_query(query)
                print(f"  => Query Type: {intent.query_type}")
                print(f"  => Entities: States={intent.entities.get('states', [])}, Crops={intent.entities.get('crops', [])}")
                
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
                
                # Format response
                response = processor.format_response(result)
                
                # Check if response is meaningful
                if len(response) < 50:
                    print(f"  [WARN] Short response ({len(response)} chars)")
                    category_results["issues"].append(f"Short response for: {query}")
                    issues_found.append({
                        "category": category,
                        "query": query,
                        "issue": "Response too short",
                        "response_length": len(response)
                    })
                elif (
                    "No data found" in response
                    or (
                        "message" in str(result.get("data", {}))
                        and intent.query_type != "clarification"
                    )
                ):
                    print(f"  [WARN] No data found")
                    category_results["issues"].append(f"No data for: {query}")
                    issues_found.append({
                        "category": category,
                        "query": query,
                        "issue": "No data found",
                        "query_type": intent.query_type
                    })
                else:
                    print(f"  [OK] Success - Response length: {len(response)} chars")
                    successful += 1
                    category_results["success"] += 1
                    
            except Exception as e:
                print(f"  [ERROR] {str(e)}")
                failed += 1
                category_results["failed"] += 1
                category_results["issues"].append(f"Error in: {query} - {str(e)}")
                issues_found.append({
                    "category": category,
                    "query": query,
                    "issue": "Exception",
                    "error": str(e)
                })
        
        results_by_category[category] = category_results
        print(f"\nCategory Summary: {category_results['success']}/{category_results['total']} successful")
    
    # Print comprehensive summary
    print("\n" + "=" * 100)
    print(" " * 35 + "FINAL SUMMARY")
    print("=" * 100)
    print(f"\nTotal Queries Tested: {total_queries}")
    print(f"Successful: {successful} ({successful/total_queries*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total_queries*100:.1f}%)")
    print(f"Issues Found: {len(issues_found)}")
    
    print("\n" + "-" * 100)
    print("CATEGORY BREAKDOWN")
    print("-" * 100)
    for category, results in results_by_category.items():
        success_rate = results['success'] / results['total'] * 100
        print(f"{category:40} {results['success']:3}/{results['total']:3} ({success_rate:5.1f}%)")
    
    # Print top issues
    if issues_found:
        print("\n" + "-" * 100)
        print("TOP ISSUES TO FIX")
        print("-" * 100)
        
        # Group issues by type
        issue_types = {}
        for issue in issues_found:
            issue_type = issue.get("issue", "Unknown")
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        for issue_type, issues in issue_types.items():
            print(f"\n{issue_type}: {len(issues)} occurrences")
            for issue in issues[:3]:  # Show first 3 examples
                print(f"  - {issue['query'][:60]}...")
    
    # Recommendations
    print("\n" + "=" * 100)
    print("RECOMMENDATIONS FOR IMPROVEMENT")
    print("=" * 100)
    
    recommendations = []
    
    # Analyze issues
    short_responses = [i for i in issues_found if i.get("issue") == "Response too short"]
    no_data_issues = [i for i in issues_found if i.get("issue") == "No data found"]
    exceptions = [i for i in issues_found if i.get("issue") == "Exception"]
    
    if short_responses:
        recommendations.append(f"1. Fix {len(short_responses)} queries producing short responses - improve response formatting")
    
    if no_data_issues:
        recommendations.append(f"2. Handle {len(no_data_issues)} 'no data found' cases - add better fallback messages")
    
    if exceptions:
        recommendations.append(f"3. Fix {len(exceptions)} exceptions - improve error handling")
    
    # Check query type distribution
    query_types_used = {}
    for issue in issues_found:
        qt = issue.get("query_type", "Unknown")
        query_types_used[qt] = query_types_used.get(qt, 0) + 1
    
    if query_types_used:
        recommendations.append(f"4. Query type issues: {query_types_used}")
    
    recommendations.append("5. Add entity extraction for more crop types and states")
    recommendations.append("6. Improve handling of vague/ambiguous queries")
    recommendations.append("7. Add graceful handling for out-of-dataset queries")
    recommendations.append("8. Enhance multi-part query understanding")
    
    for rec in recommendations:
        print(f"  {rec}")
    
    print("\n" + "=" * 100)
    print("TEST COMPLETE!")
    print("=" * 100)
    
    return {
        "total": total_queries,
        "successful": successful,
        "failed": failed,
        "issues": issues_found,
        "recommendations": recommendations
    }


if __name__ == "__main__":
    results = run_comprehensive_test()
    
    # Save results to file
    output_file = Path(__file__).parent.parent / "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
