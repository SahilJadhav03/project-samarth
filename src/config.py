"""
Configuration file for Project Samarth
"""

# Data.gov.in API Configuration
DATA_GOV_API_BASE = "https://api.data.gov.in/resource"
DATA_GOV_API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"  # Example key

# Dataset IDs from data.gov.in
DATASETS = {
    "crop_production": {
        "id": "9ef84268-d588-465a-a308-a864a43d0070",
        "name": "District-wise, Season-wise Crop Production Statistics",
        "ministry": "Ministry of Agriculture & Farmers Welfare"
    },
    "rainfall": {
        "id": "d2c3e882-15d4-4a2e-89e0-ff56f19e9f56",
        "name": "Rainfall Data - India Meteorological Department",
        "ministry": "India Meteorological Department"
    },
    "state_wise_rainfall": {
        "id": "b4c3e882-15d4-4a2e-89e0-ff56f19e9f88",
        "name": "State-wise Annual Rainfall",
        "ministry": "India Meteorological Department"
    }
}

# LLM Configuration (Using OpenAI or local models)
LLM_MODEL = "gpt-4"  # Can be changed to local models for data sovereignty
LLM_TEMPERATURE = 0.1  # Low temperature for factual accuracy

# System Configuration
CACHE_DIR = "./data_cache"
MAX_RETRIES = 3
TIMEOUT = 30
