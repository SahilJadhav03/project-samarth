"""
Data Discovery Module for Project Samarth
Explores data.gov.in portal and catalogs available datasets
"""

import requests
import pandas as pd
import json
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataGovExplorer:
    """
    Explores and catalogs datasets from data.gov.in
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.catalog_base = "https://data.gov.in/api/datastore/resource.json"
        self.search_base = "https://data.gov.in/api/catalog/search"
        
    def search_datasets(self, query: str, ministry: str = None) -> List[Dict]:
        """
        Search for datasets on data.gov.in
        
        Args:
            query: Search keywords (e.g., "agriculture", "rainfall", "crop production")
            ministry: Filter by ministry name
            
        Returns:
            List of dataset metadata
        """
        params = {
            "q": query,
            "format": "json"
        }
        
        if ministry:
            params["ministry"] = ministry
        
        try:
            response = requests.get(self.search_base, params=params, timeout=30)
            response.raise_for_status()
            
            results = response.json()
            datasets = results.get("results", [])
            
            logger.info(f"Found {len(datasets)} datasets for query: {query}")
            return datasets
            
        except Exception as e:
            logger.error(f"Error searching datasets: {e}")
            return []
    
    def get_dataset_info(self, resource_id: str) -> Dict:
        """
        Get detailed information about a specific dataset
        
        Args:
            resource_id: The unique resource ID from data.gov.in
            
        Returns:
            Dataset metadata and structure information
        """
        params = {
            "resource_id": resource_id,
            "api-key": self.api_key,
            "limit": 5  # Just get a few records to understand structure
        }
        
        try:
            response = requests.get(self.catalog_base, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            info = {
                "resource_id": resource_id,
                "total_records": data.get("total", 0),
                "fields": [],
                "sample_records": data.get("records", [])
            }
            
            # Extract field information
            if data.get("records"):
                sample = data["records"][0]
                info["fields"] = list(sample.keys())
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting dataset info: {e}")
            return {}
    
    def discover_agriculture_datasets(self) -> List[Dict]:
        """
        Discover datasets from Ministry of Agriculture & Farmers Welfare
        """
        logger.info("Discovering Agriculture datasets...")
        
        queries = [
            "crop production",
            "district wise crop",
            "agricultural statistics",
            "crop yield",
            "area production yield"
        ]
        
        all_datasets = []
        for query in queries:
            datasets = self.search_datasets(
                query=query,
                ministry="Ministry of Agriculture and Farmers Welfare"
            )
            all_datasets.extend(datasets)
        
        # Remove duplicates
        unique_datasets = {d.get("resource_id"): d for d in all_datasets if d.get("resource_id")}
        return list(unique_datasets.values())
    
    def discover_climate_datasets(self) -> List[Dict]:
        """
        Discover datasets from India Meteorological Department
        """
        logger.info("Discovering Climate/IMD datasets...")
        
        queries = [
            "rainfall",
            "climate data",
            "meteorological",
            "precipitation",
            "weather data"
        ]
        
        all_datasets = []
        for query in queries:
            datasets = self.search_datasets(query=query)
            # Filter for IMD or climate-related
            climate_datasets = [
                d for d in datasets 
                if any(keyword in str(d).lower() for keyword in ["imd", "meteorolog", "rainfall", "climate"])
            ]
            all_datasets.extend(climate_datasets)
        
        unique_datasets = {d.get("resource_id"): d for d in all_datasets if d.get("resource_id")}
        return list(unique_datasets.values())


class DataStructureAnalyzer:
    """
    Analyzes different data structures and creates mapping strategies
    """
    
    @staticmethod
    def analyze_crop_data_structure(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze structure of crop production datasets
        Identifies: state columns, district columns, crop names, production values, years
        """
        analysis = {
            "total_records": len(df),
            "columns": list(df.columns),
            "structure_type": "unknown",
            "mappings": {}
        }
        
        # Common column name variations for different fields
        state_patterns = ["state", "state_name", "state name", "statename"]
        district_patterns = ["district", "district_name", "district name", "districtname"]
        crop_patterns = ["crop", "crop_name", "crop name", "cropname", "commodity"]
        year_patterns = ["year", "crop_year", "crop year", "season_year", "yr"]
        production_patterns = ["production", "prod", "quantity", "output"]
        area_patterns = ["area", "area_hectare", "hectares"]
        
        # Find matching columns
        cols_lower = {col.lower(): col for col in df.columns}
        
        for pattern in state_patterns:
            if pattern in cols_lower:
                analysis["mappings"]["state"] = cols_lower[pattern]
                break
        
        for pattern in district_patterns:
            if pattern in cols_lower:
                analysis["mappings"]["district"] = cols_lower[pattern]
                break
        
        for pattern in crop_patterns:
            if pattern in cols_lower:
                analysis["mappings"]["crop"] = cols_lower[pattern]
                break
        
        for pattern in year_patterns:
            if pattern in cols_lower:
                analysis["mappings"]["year"] = cols_lower[pattern]
                break
        
        for pattern in production_patterns:
            if pattern in cols_lower:
                analysis["mappings"]["production"] = cols_lower[pattern]
                break
        
        for pattern in area_patterns:
            if pattern in cols_lower:
                analysis["mappings"]["area"] = cols_lower[pattern]
                break
        
        # Determine structure type
        required_fields = ["state", "crop", "production"]
        if all(field in analysis["mappings"] for field in required_fields):
            analysis["structure_type"] = "crop_production"
        
        # Sample values
        analysis["sample_values"] = {}
        for field, col in analysis["mappings"].items():
            if col in df.columns:
                analysis["sample_values"][field] = df[col].dropna().unique()[:5].tolist()
        
        return analysis
    
    @staticmethod
    def analyze_rainfall_data_structure(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze structure of rainfall/climate datasets
        """
        analysis = {
            "total_records": len(df),
            "columns": list(df.columns),
            "structure_type": "unknown",
            "mappings": {}
        }
        
        # Common patterns
        state_patterns = ["state", "state_name", "subdivision", "region"]
        year_patterns = ["year", "yr", "annual"]
        rainfall_patterns = ["rainfall", "precipitation", "rain", "annual_rainfall", "total_rainfall"]
        month_patterns = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        
        cols_lower = {col.lower(): col for col in df.columns}
        
        for pattern in state_patterns:
            if pattern in cols_lower:
                analysis["mappings"]["state"] = cols_lower[pattern]
                break
        
        for pattern in year_patterns:
            if pattern in cols_lower:
                analysis["mappings"]["year"] = cols_lower[pattern]
                break
        
        for pattern in rainfall_patterns:
            if pattern in cols_lower:
                analysis["mappings"]["rainfall"] = cols_lower[pattern]
                break
        
        # Check for monthly data
        monthly_cols = []
        for month in month_patterns:
            if month in cols_lower:
                monthly_cols.append(cols_lower[month])
        
        if monthly_cols:
            analysis["mappings"]["monthly_data"] = monthly_cols
            analysis["has_monthly_breakdown"] = True
        else:
            analysis["has_monthly_breakdown"] = False
        
        # Determine structure type
        if "state" in analysis["mappings"] and "rainfall" in analysis["mappings"]:
            analysis["structure_type"] = "climate_data"
        
        # Sample values
        analysis["sample_values"] = {}
        for field, col in analysis["mappings"].items():
            if isinstance(col, list):
                continue
            if col in df.columns:
                analysis["sample_values"][field] = df[col].dropna().unique()[:5].tolist()
        
        return analysis
    
    @staticmethod
    def create_unified_schema(crop_analysis: Dict, rainfall_analysis: Dict) -> Dict:
        """
        Create a unified schema for joining crop and rainfall data
        """
        schema = {
            "join_keys": [],
            "crop_mappings": crop_analysis.get("mappings", {}),
            "rainfall_mappings": rainfall_analysis.get("mappings", {}),
            "normalization_required": []
        }
        
        # Identify common join keys
        if "state" in crop_analysis.get("mappings", {}) and "state" in rainfall_analysis.get("mappings", {}):
            schema["join_keys"].append("state")
        
        if "year" in crop_analysis.get("mappings", {}) and "year" in rainfall_analysis.get("mappings", {}):
            schema["join_keys"].append("year")
        
        # Identify fields needing normalization
        crop_states = set(crop_analysis.get("sample_values", {}).get("state", []))
        rainfall_states = set(rainfall_analysis.get("sample_values", {}).get("state", []))
        
        if crop_states and rainfall_states:
            if crop_states != rainfall_states:
                schema["normalization_required"].append({
                    "field": "state",
                    "reason": "Different state name formats",
                    "crop_format": list(crop_states)[:3],
                    "rainfall_format": list(rainfall_states)[:3]
                })
        
        return schema


def run_data_discovery():
    """
    Run comprehensive data discovery process
    """
    print("=" * 80)
    print("DATA.GOV.IN DISCOVERY & INTEGRATION ANALYSIS")
    print("=" * 80)
    
    # Note: Using a public API key for demonstration
    api_key = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
    
    explorer = DataGovExplorer(api_key)
    
    print("\n📊 PHASE 1: DISCOVERING AGRICULTURE DATASETS")
    print("-" * 80)
    
    ag_datasets = explorer.discover_agriculture_datasets()
    
    print(f"\nFound {len(ag_datasets)} agriculture-related datasets")
    if ag_datasets:
        print("\nTop 5 Agriculture Datasets:")
        for i, ds in enumerate(ag_datasets[:5], 1):
            print(f"{i}. {ds.get('title', 'N/A')}")
            print(f"   Resource ID: {ds.get('resource_id', 'N/A')}")
            print(f"   Source: {ds.get('source', 'N/A')}")
            print()
    
    print("\n🌧️ PHASE 2: DISCOVERING CLIMATE/IMD DATASETS")
    print("-" * 80)
    
    climate_datasets = explorer.discover_climate_datasets()
    
    print(f"\nFound {len(climate_datasets)} climate-related datasets")
    if climate_datasets:
        print("\nTop 5 Climate Datasets:")
        for i, ds in enumerate(climate_datasets[:5], 1):
            print(f"{i}. {ds.get('title', 'N/A')}")
            print(f"   Resource ID: {ds.get('resource_id', 'N/A')}")
            print(f"   Source: {ds.get('source', 'N/A')}")
            print()
    
    print("\n🔍 PHASE 3: ANALYZING DATA STRUCTURES")
    print("-" * 80)
    
    # Analyze using our synthetic data to demonstrate the concept
    from data_integration import SyntheticDataGenerator
    
    crop_df = SyntheticDataGenerator.generate_crop_production_data()
    rainfall_df = SyntheticDataGenerator.generate_rainfall_data()
    
    analyzer = DataStructureAnalyzer()
    
    print("\n📋 Crop Data Structure Analysis:")
    crop_analysis = analyzer.analyze_crop_data_structure(crop_df)
    print(json.dumps(crop_analysis, indent=2, default=str))
    
    print("\n☔ Rainfall Data Structure Analysis:")
    rainfall_analysis = analyzer.analyze_rainfall_data_structure(rainfall_df)
    print(json.dumps(rainfall_analysis, indent=2, default=str))
    
    print("\n🔗 PHASE 4: CREATING UNIFIED SCHEMA")
    print("-" * 80)
    
    unified_schema = analyzer.create_unified_schema(crop_analysis, rainfall_analysis)
    print("\nUnified Integration Schema:")
    print(json.dumps(unified_schema, indent=2, default=str))
    
    print("\n" + "=" * 80)
    print("KEY CHALLENGES IDENTIFIED:")
    print("=" * 80)
    
    challenges = [
        {
            "challenge": "Different Column Names",
            "example": "Crop data uses 'state_name', Climate uses 'subdivision'",
            "solution": "Dynamic column mapping with pattern matching"
        },
        {
            "challenge": "Inconsistent State Names",
            "example": "Crop: 'PUNJAB', Climate: 'Punjab', 'PUNJAB AND CHANDIGARH'",
            "solution": "Normalization dictionary with fuzzy matching"
        },
        {
            "challenge": "Different Time Granularity",
            "example": "Crop: 'Kharif 2022', Climate: '2022'",
            "solution": "Temporal alignment and aggregation"
        },
        {
            "challenge": "Missing Data Fields",
            "example": "Some datasets lack district-level granularity",
            "solution": "Multi-level aggregation (district→state→national)"
        },
        {
            "challenge": "Different Data Formats",
            "example": "JSON, CSV, XML across different APIs",
            "solution": "Format-agnostic parsers with automatic detection"
        }
    ]
    
    for i, challenge in enumerate(challenges, 1):
        print(f"\n{i}. {challenge['challenge']}")
        print(f"   Example: {challenge['example']}")
        print(f"   Solution: {challenge['solution']}")
    
    print("\n" + "=" * 80)
    print("✅ DATA DISCOVERY COMPLETE")
    print("=" * 80)
    print("\nOur system handles these challenges through:")
    print("  • Flexible column mapping")
    print("  • State name normalization")
    print("  • Temporal alignment")
    print("  • Multi-level aggregation")
    print("  • Smart caching for performance")
    print("  • Graceful fallback mechanisms")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    run_data_discovery()
