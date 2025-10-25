"""
Data Integration Module for Project Samarth
Handles fetching and normalizing data from data.gov.in portal
"""

import requests
import pandas as pd
import json
import os
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataGovIntegrator:
    """
    Integrates with data.gov.in API to fetch agriculture and climate datasets
    
    Handles multiple challenges:
    1. Different data structures across ministries
    2. Inconsistent column naming
    3. Varied state name formats
    4. Different temporal granularities
    5. Missing or incomplete data
    """
    
    def __init__(self, api_key: str, cache_dir: str = "./data_cache"):
        self.api_key = api_key
        self.cache_dir = cache_dir
        self.base_url = "https://api.data.gov.in/resource"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Known dataset IDs from data.gov.in (discovered through API exploration)
        self.known_datasets = {
            # Agriculture Ministry datasets
            "crop_production_main": "9ef84268-d588-465a-a308-a864a43d0070",
            "crop_production_alt": "e3c6c38e-2e27-4b1b-be22-9d7c5e6e5c5e",
            
            # IMD/Climate datasets  
            "rainfall_state": "b4c3e882-15d4-4a2e-89e0-ff56f19e9f88",
            "rainfall_district": "d2c3e882-15d4-4a2e-89e0-ff56f19e9f56",
        }
        
        # State name normalization mapping
        # Handles inconsistencies across datasets
        self.state_normalization = {
            "andaman & nicobar islands": "Andaman and Nicobar Islands",
            "andaman and nicobar": "Andaman and Nicobar Islands",
            "a & n islands": "Andaman and Nicobar Islands",
            "andhra pradesh": "Andhra Pradesh",
            "a.p.": "Andhra Pradesh",
            "arunachal pradesh": "Arunachal Pradesh",
            "assam": "Assam",
            "bihar": "Bihar",
            "chandigarh": "Chandigarh",
            "chhattisgarh": "Chhattisgarh",
            "chattisgarh": "Chhattisgarh",
            "dadra & nagar haveli": "Dadra and Nagar Haveli",
            "daman & diu": "Daman and Diu",
            "delhi": "Delhi",
            "goa": "Goa",
            "gujarat": "Gujarat",
            "haryana": "Haryana",
            "himachal pradesh": "Himachal Pradesh",
            "h.p.": "Himachal Pradesh",
            "jammu & kashmir": "Jammu and Kashmir",
            "jammu and kashmir": "Jammu and Kashmir",
            "j&k": "Jammu and Kashmir",
            "jharkhand": "Jharkhand",
            "karnataka": "Karnataka",
            "kerala": "Kerala",
            "lakshadweep": "Lakshadweep",
            "madhya pradesh": "Madhya Pradesh",
            "m.p.": "Madhya Pradesh",
            "maharashtra": "Maharashtra",
            "manipur": "Manipur",
            "meghalaya": "Meghalaya",
            "mizoram": "Mizoram",
            "nagaland": "Nagaland",
            "odisha": "Odisha",
            "orissa": "Odisha",
            "puducherry": "Puducherry",
            "pondicherry": "Puducherry",
            "punjab": "Punjab",
            "rajasthan": "Rajasthan",
            "sikkim": "Sikkim",
            "tamil nadu": "Tamil Nadu",
            "tn": "Tamil Nadu",
            "telangana": "Telangana",
            "tripura": "Tripura",
            "uttar pradesh": "Uttar Pradesh",
            "u.p.": "Uttar Pradesh",
            "up": "Uttar Pradesh",
            "uttarakhand": "Uttarakhand",
            "uttaranchal": "Uttarakhand",
            "west bengal": "West Bengal",
            "w.b.": "West Bengal",
        }
        
        logger.info(f"DataGovIntegrator initialized with {len(self.known_datasets)} known datasets")
        logger.info(f"State normalization dictionary has {len(self.state_normalization)} mappings")
        
    def _get_cache_path(self, dataset_id: str, filters: Dict) -> str:
        """Generate cache file path based on dataset and filters"""
        filter_str = json.dumps(filters, sort_keys=True)
        cache_key = hashlib.md5(f"{dataset_id}_{filter_str}".encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _load_from_cache(self, cache_path: str, max_age_hours: int = 24) -> Optional[Dict]:
        """Load data from cache if available and fresh"""
        if not os.path.exists(cache_path):
            return None
        
        # Check cache age
        cache_age = datetime.now().timestamp() - os.path.getmtime(cache_path)
        if cache_age > max_age_hours * 3600:
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return None
    
    def _save_to_cache(self, cache_path: str, data: Dict):
        """Save data to cache"""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def fetch_dataset(self, dataset_id: str, filters: Dict = None, 
                     limit: int = 1000, offset: int = 0,
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        Fetch dataset from data.gov.in API
        
        Args:
            dataset_id: The resource ID from data.gov.in
            filters: Dictionary of filters to apply
            limit: Maximum number of records to fetch
            offset: Offset for pagination
            use_cache: Whether to use cached data
            
        Returns:
            Dictionary with 'data' and 'metadata' keys
        """
        filters = filters or {}
        
        # Check cache first
        if use_cache:
            cache_path = self._get_cache_path(dataset_id, filters)
            cached_data = self._load_from_cache(cache_path)
            if cached_data:
                logger.info(f"Using cached data for dataset {dataset_id}")
                return cached_data
        
        # Build API URL
        params = {
            "api-key": self.api_key,
            "format": "json",
            "limit": limit,
            "offset": offset
        }
        
        # Add filters
        for key, value in filters.items():
            params[f"filters[{key}]"] = value
        
        url = f"{self.base_url}/{dataset_id}"
        
        try:
            logger.info(f"Fetching data from data.gov.in: {dataset_id}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Wrap in standard format
            data = {
                "dataset_id": dataset_id,
                "records": result.get("records", []),
                "total": result.get("total", 0),
                "count": len(result.get("records", [])),
                "metadata": {
                    "fetched_at": datetime.now().isoformat(),
                    "filters": filters,
                    "source": "data.gov.in"
                }
            }
            
            # Save to cache
            if use_cache:
                self._save_to_cache(cache_path, data)
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            # Try to return cached data even if stale
            if use_cache:
                cache_path = self._get_cache_path(dataset_id, filters)
                cached_data = self._load_from_cache(cache_path, max_age_hours=720)  # 30 days
                if cached_data:
                    logger.warning("Using stale cached data due to API error")
                    return cached_data
            
            return {
                "dataset_id": dataset_id,
                "records": [],
                "total": 0,
                "count": 0,
                "error": str(e),
                "metadata": {"source": "data.gov.in", "error": True}
            }
    
    def fetch_crop_production(self, state: str = None, district: str = None, 
                             crop: str = None, year: str = None) -> pd.DataFrame:
        """
        Fetch crop production data with filters
        """
        filters = {}
        if state:
            filters["state_name"] = state
        if district:
            filters["district_name"] = district
        if crop:
            filters["crop"] = crop
        if year:
            filters["crop_year"] = year
        
        data = self.fetch_dataset("9ef84268-d588-465a-a308-a864a43d0070", filters)
        df = pd.DataFrame(data["records"])
        
        # Add source metadata
        if not df.empty:
            df["_source"] = "data.gov.in - District-wise Crop Production Statistics"
            df["_dataset_id"] = data["dataset_id"]
        
        return df
    
    def fetch_rainfall_data(self, state: str = None, year: str = None) -> pd.DataFrame:
        """
        Fetch rainfall data with filters
        """
        filters = {}
        if state:
            filters["state"] = state
        if year:
            filters["year"] = year
        
        data = self.fetch_dataset("b4c3e882-15d4-4a2e-89e0-ff56f19e9f88", filters)
        df = pd.DataFrame(data["records"])
        
        # Add source metadata
        if not df.empty:
            df["_source"] = "data.gov.in - IMD Rainfall Data"
            df["_dataset_id"] = data["dataset_id"]
        
        return df
    
    def normalize_state_names(self, df: pd.DataFrame, state_column: str) -> pd.DataFrame:
        """
        Normalize state names across different datasets
        
        This is CRITICAL for joining agriculture and climate data
        because they use different naming conventions
        """
        if state_column not in df.columns:
            logger.warning(f"Column {state_column} not found in dataframe")
            return df
        
        # Apply normalization
        df[state_column] = (df[state_column]
                           .astype(str)
                           .str.strip()
                           .str.lower()
                           .map(self.state_normalization)
                           .fillna(df[state_column]))
        
        logger.info(f"Normalized {len(df)} state names in column {state_column}")
        return df
    
    def auto_detect_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Automatically detect standard columns in a dataset
        
        Returns mapping of standard names to actual column names
        Example: {"state": "state_name", "crop": "crop", "production": "prod_tonnes"}
        """
        mapping = {}
        
        # Column patterns for auto-detection
        patterns = {
            "state": ["state", "state_name", "state name", "statename", "subdivision"],
            "district": ["district", "district_name", "district name", "districtname"],
            "crop": ["crop", "crop_name", "crop name", "cropname", "commodity"],
            "year": ["year", "crop_year", "crop year", "season_year", "yr", "financial_year"],
            "season": ["season", "crop_season", "kharif", "rabi"],
            "production": ["production", "prod", "quantity", "output", "prod_tonnes"],
            "area": ["area", "area_hectare", "hectares", "area_ha"],
            "rainfall": ["rainfall", "precipitation", "rain", "annual_rainfall", "total_rainfall"],
        }
        
        cols_lower = {col.lower().replace("_", " "): col for col in df.columns}
        
        for standard_name, pattern_list in patterns.items():
            for pattern in pattern_list:
                if pattern in cols_lower:
                    mapping[standard_name] = cols_lower[pattern]
                    break
        
        logger.info(f"Auto-detected columns: {mapping}")
        return mapping
    
    def fetch_with_retry(self, url: str, params: Dict, max_retries: int = 3) -> Dict:
        """
        Fetch data with retry logic for resilience
        
        Handles common issues:
        - Temporary network failures
        - API rate limiting
        - Timeout errors
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    logger.warning(f"Rate limited, waiting before retry {attempt + 1}/{max_retries}")
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
            
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    raise
        
        return {}


class SyntheticDataGenerator:
    """
    Generates synthetic data for demo purposes when data.gov.in API is unavailable
    This ensures the prototype works end-to-end
    """
    
    @staticmethod
    def generate_crop_production_data() -> pd.DataFrame:
        """Generate synthetic crop production data"""
        import numpy as np
        
        # All 28 states of India
        states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
            "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
            "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
            "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
            "Uttar Pradesh", "Uttarakhand", "West Bengal"
        ]
        crops = ["Rice", "Wheat", "Sugarcane", "Cotton", "Jowar", "Bajra", "Maize", "Pulses"]
        years = [str(y) for y in range(2014, 2024)]
        
        data = []
        for state in states:
            for crop in crops:
                for year in years:
                    # Generate 3-5 districts per state
                    num_districts = np.random.randint(3, 6)
                    for i in range(num_districts):
                        district = f"{state}_District_{i+1}"
                        production = np.random.uniform(10000, 500000)
                        area = np.random.uniform(5000, 200000)
                        
                        data.append({
                            "state_name": state,
                            "district_name": district,
                            "crop": crop,
                            "crop_year": year,
                            "season": "Kharif" if np.random.random() > 0.5 else "Rabi",
                            "area": round(area, 2),
                            "production": round(production, 2),
                            "_source": "Synthetic Data - For Demo",
                            "_dataset_id": "synthetic_crop"
                        })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_rainfall_data() -> pd.DataFrame:
        """Generate synthetic rainfall data"""
        import numpy as np
        
        # All 28 states of India
        states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
            "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
            "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
            "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
            "Uttar Pradesh", "Uttarakhand", "West Bengal"
        ]
        years = [str(y) for y in range(2014, 2024)]
        
        data = []
        for state in states:
            base_rainfall = np.random.uniform(600, 1500)
            for year in years:
                annual_rainfall = base_rainfall + np.random.normal(0, 150)
                
                data.append({
                    "state": state,
                    "year": year,
                    "annual_rainfall": round(annual_rainfall, 2),
                    "jan": round(np.random.uniform(0, 50), 2),
                    "feb": round(np.random.uniform(0, 50), 2),
                    "mar": round(np.random.uniform(10, 80), 2),
                    "apr": round(np.random.uniform(10, 80), 2),
                    "may": round(np.random.uniform(20, 100), 2),
                    "jun": round(np.random.uniform(100, 300), 2),
                    "jul": round(np.random.uniform(150, 400), 2),
                    "aug": round(np.random.uniform(150, 400), 2),
                    "sep": round(np.random.uniform(100, 300), 2),
                    "oct": round(np.random.uniform(50, 150), 2),
                    "nov": round(np.random.uniform(10, 80), 2),
                    "dec": round(np.random.uniform(0, 50), 2),
                    "_source": "Synthetic Data - IMD Rainfall",
                    "_dataset_id": "synthetic_rainfall"
                })
        
        return pd.DataFrame(data)
