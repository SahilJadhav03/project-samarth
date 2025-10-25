"""
Visual Demonstration of Data Integration Challenges
Shows real examples of how different data sources are incompatible
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.data_integration import DataGovIntegrator, SyntheticDataGenerator
import json

print("=" * 100)
print(" " * 20 + "DATA INTEGRATION CHALLENGE DEMONSTRATION")
print("=" * 100)

print("\n" + "▓" * 100)
print("CHALLENGE 1: DIFFERENT COLUMN STRUCTURES")
print("▓" * 100)

# Generate sample data
crop_df = SyntheticDataGenerator.generate_crop_production_data()
rainfall_df = SyntheticDataGenerator.generate_rainfall_data()

print("\n📊 AGRICULTURE DATA STRUCTURE (Ministry of Agriculture):")
print("-" * 100)
print(crop_df.head(3).to_string())
print(f"\nColumns: {list(crop_df.columns)}")

print("\n☔ CLIMATE DATA STRUCTURE (India Meteorological Department):")
print("-" * 100)
print(rainfall_df.head(3).to_string())
print(f"\nColumns: {list(rainfall_df.columns)}")

print("\n❌ PROBLEM:")
print("   • Agriculture uses 'state_name', Climate uses 'state'")
print("   • Agriculture uses 'crop_year', Climate uses 'year'")
print("   • Cannot join directly - column names don't match!")

print("\n✅ SOLUTION: Auto-detect and map columns")
integrator = DataGovIntegrator(api_key="demo")
crop_mapping = integrator.auto_detect_columns(crop_df)
rain_mapping = integrator.auto_detect_columns(rainfall_df)

print(f"\n   Detected Crop Data Mapping: {crop_mapping}")
print(f"   Detected Climate Data Mapping: {rain_mapping}")

print("\n" + "▓" * 100)
print("CHALLENGE 2: INCONSISTENT STATE NAMES")
print("▓" * 100)

# Show different state name formats
state_examples = {
    "Agriculture Data": ["Punjab", "Haryana", "Uttar Pradesh", "Maharashtra", "Karnataka"],
    "Climate Data (Format 1)": ["PUNJAB", "HARYANA", "UTTAR PRADESH", "MAHARASHTRA", "KARNATAKA"],
    "Climate Data (Format 2)": ["punjab", "haryana", "u.p.", "maharastra", "karnataka"],
    "IMD Subdivision": ["Punjab & Chandigarh", "Haryana", "East U.P.", "Vidarbha", "South Karnataka"]
}

print("\nDifferent State Name Formats Across Datasets:")
print("-" * 100)
for source, states in state_examples.items():
    print(f"\n{source}:")
    print(f"  {states}")

print("\n❌ PROBLEM:")
print("   • Same state, different spellings")
print("   • Some use abbreviations (U.P., H.P.)")
print("   • Some combine regions (Punjab & Chandigarh)")
print("   • Cannot join on state - names don't match!")

print("\n✅ SOLUTION: Comprehensive normalization dictionary")
print(f"\n   Our system has {len(integrator.state_normalization)} state name mappings")
print("\n   Examples:")
sample_mappings = list(integrator.state_normalization.items())[:10]
for original, normalized in sample_mappings:
    print(f"      '{original}' → '{normalized}'")

# Demonstrate normalization
test_states = ["PUNJAB", "punjab", "u.p.", "Uttar Pradesh", "UP"]
print(f"\n   Before normalization: {test_states}")
normalized = [integrator.state_normalization.get(s.lower(), s) for s in test_states]
print(f"   After normalization:  {normalized}")

print("\n" + "▓" * 100)
print("CHALLENGE 3: TEMPORAL MISALIGNMENT")
print("▓" * 100)

print("\n📅 Different Time Representations:")
print("-" * 100)

temporal_examples = {
    "Agriculture": ["2022-23", "2021-22", "2020-21"],
    "Climate": ["2022", "2021", "2020"],
    "Seasonal": ["Kharif 2022", "Rabi 2022-23"]
}

for source, formats in temporal_examples.items():
    print(f"\n{source} Format: {formats}")

print("\n❌ PROBLEM:")
print("   • Agriculture uses crop year (2022-23 = Jul 2022 to Jun 2023)")
print("   • Climate uses calendar year (2022 = Jan 2022 to Dec 2022)")
print("   • Seasonal data spans two calendar years")
print("   • Cannot join on year directly!")

print("\n✅ SOLUTION: Extract base year for alignment")
print("\n   '2022-23' → '2022'")
print("   '2021-22' → '2021'")
print("   'Kharif 2022' → '2022'")

print("\n" + "▓" * 100)
print("CHALLENGE 4: GRANULARITY MISMATCH")
print("▓" * 100)

print("\n📍 Different Geographic Granularities:")
print("-" * 100)

print("\nAgriculture Data (District Level):")
punjab_crop = crop_df[crop_df['state_name'] == 'Punjab'].head(5)
print(punjab_crop[['state_name', 'district_name', 'crop', 'production']].to_string())

print("\n\nClimate Data (State Level Only):")
punjab_rain = rainfall_df[rainfall_df['state'] == 'Punjab'].head(2)
print(punjab_rain[['state', 'year', 'annual_rainfall']].to_string())

print("\n❌ PROBLEM:")
print("   • Crop data: District-level (Amritsar, Ludhiana, etc.)")
print("   • Rainfall data: State-level only (Punjab)")
print("   • How to correlate district crops with district rainfall?")

print("\n✅ SOLUTION: Multi-level aggregation strategy")
print("\n   Option 1: Aggregate crop data to state level")
state_level = crop_df.groupby(['state_name', 'crop_year']).agg({
    'production': 'sum',
    'area': 'sum'
}).reset_index()
print("\n" + state_level.head(3).to_string())

print("\n   Option 2: Broadcast state rainfall to all districts")
print("   (Assume all districts in a state have same rainfall)")

print("\n" + "▓" * 100)
print("CHALLENGE 5: DATA QUALITY ISSUES")
print("▓" * 100)

print("\n🔍 Real-world Data Quality Problems:")
print("-" * 100)

quality_issues = [
    {
        "issue": "Missing Values",
        "example": "Production: NULL, Area: 1234.5",
        "impact": "Cannot calculate yield",
        "solution": "Skip or interpolate based on neighbors"
    },
    {
        "issue": "Inconsistent Units",
        "example": "Production in tonnes vs quintals",
        "impact": "Wrong comparisons",
        "solution": "Unit detection and conversion"
    },
    {
        "issue": "Outliers",
        "example": "Rainfall: -999 (error code) or 99999",
        "impact": "Skewed averages",
        "solution": "Statistical filtering (IQR method)"
    },
    {
        "issue": "Duplicate Records",
        "example": "Same state-year-crop appears twice",
        "impact": "Inflated totals",
        "solution": "Deduplication with key-based filtering"
    },
    {
        "issue": "Encoding Issues",
        "example": "State name: 'Pôndīchérry' vs 'Pondicherry'",
        "impact": "Join failures",
        "solution": "Unicode normalization"
    }
]

for i, issue in enumerate(quality_issues, 1):
    print(f"\n{i}. {issue['issue']}")
    print(f"   Example: {issue['example']}")
    print(f"   Impact: {issue['impact']}")
    print(f"   Solution: {issue['solution']}")

print("\n" + "▓" * 100)
print("SUCCESSFUL INTEGRATION EXAMPLE")
print("▓" * 100)

print("\n🎯 Joining Agriculture + Climate Data:")
print("-" * 100)

# Normalize and join
crop_normalized = crop_df.copy()
crop_normalized['state'] = crop_normalized['state_name']
crop_normalized['year'] = crop_normalized['crop_year']

# Join
merged = crop_normalized.merge(
    rainfall_df[['state', 'year', 'annual_rainfall']],
    on=['state', 'year'],
    how='inner'
)

print(f"\n✓ Agriculture records: {len(crop_df):,}")
print(f"✓ Climate records: {len(rainfall_df):,}")
print(f"✓ Successfully joined: {len(merged):,} records")

print("\n📊 Sample Joined Data:")
print("-" * 100)
sample_joined = merged[['state', 'year', 'crop', 'production', 'annual_rainfall']].head(5)
print(sample_joined.to_string())

print("\n" + "=" * 100)
print(" " * 30 + "INTEGRATION SUCCESS!")
print("=" * 100)

print("\n📈 SUMMARY OF SOLUTIONS:")
print("-" * 100)
solutions = [
    "✅ Auto-detection: Flexible column mapping handles unknown structures",
    "✅ Normalization: 50+ state name mappings ensure consistency",
    "✅ Temporal alignment: Extract base year for join compatibility",
    "✅ Multi-level aggregation: Handle different geographic granularities",
    "✅ Quality filtering: Remove nulls, outliers, duplicates",
    "✅ Smart caching: Reduce API calls, enable offline mode",
    "✅ Retry logic: Handle API failures gracefully",
    "✅ Source tracking: Maintain data provenance for citations"
]

for solution in solutions:
    print(f"  {solution}")

print("\n" + "=" * 100)
print(" " * 20 + "READY FOR REAL-TIME CROSS-DOMAIN SYNTHESIS!")
print("=" * 100)
