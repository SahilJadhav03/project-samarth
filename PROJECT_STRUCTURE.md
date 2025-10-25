# Project Samarth - Folder Structure

## Overview
This document describes the complete folder structure of Project Samarth, an intelligent multi-turn Q&A system for data.gov.in datasets.

## Directory Tree

```
Project Samarth/
│
├── app.py                          # Main Streamlit web application (multi-turn chat interface)
├── requirements.txt                # Python package dependencies
├── README.md                       # Main project documentation
├── PROJECT_STRUCTURE.md            # This file - folder structure documentation
│
├── src/                            # Source code directory
│   ├── __init__.py                 # Package initialization
│   ├── config.py                   # Configuration and dataset IDs
│   ├── data_integration.py         # Data fetching, normalization, and caching
│   ├── query_engine.py             # Query routing and processing logic
│   └── data_discovery.py           # Dataset exploration tools
│
├── tests/                          # Test suite directory
│   ├── __init__.py                 # Package initialization
│   ├── test_system.py              # System integration tests
│   └── test_multi_question.py      # Multi-turn conversation tests
│
├── demos/                          # Demo scripts directory
│   ├── __init__.py                 # Package initialization
│   └── demo_integration_challenges.py  # Data integration challenge demonstrations
│
├── docs/                           # Documentation directory
│   ├── PHASE1_IMPLEMENTATION.md    # Phase 1: Data integration challenges report
│   ├── PHASE2_IMPLEMENTATION.md    # Phase 2: Q&A system implementation report
│   ├── MULTI_TURN_FEATURES.md      # Multi-turn chat capability documentation
│   ├── VIDEO_DEMO_SCRIPT.md        # Video demonstration script
│   └── FINAL_VIDEO_GUIDE.md        # 2-minute video recording guide
│
├── data_cache/                     # Cache directory for API responses
│   └── (cached JSON files)         # Hashed cache files for offline operation
│
├── .venv/                          # Python virtual environment (auto-generated)
│   └── (Python packages)
│
└── __pycache__/                    # Python bytecode cache (auto-generated)
    └── (*.pyc files)
```

## Core Files Description

### Root Level

#### **app.py**
- **Purpose**: Main entry point for the web interface
- **Technology**: Streamlit multi-turn chat application
- **Features**:
  - Session state management for conversation history
  - Message history display with user/assistant avatars
  - Question counter and chat clearing functionality
  - Integration with data integration and query engine modules
  - Sample questions and quick actions
  - Source citation display

#### **requirements.txt**
- **Purpose**: Python package dependencies
- **Contents**:
  ```
  streamlit==1.29.0
  pandas==2.2.3
  numpy==1.26.4
  requests==2.31.0
  openpyxl==3.1.2
  ```

#### **README.md**
- **Purpose**: Main project documentation
- **Sections**: Overview, architecture, features, setup, usage, design decisions

#### **PROJECT_STRUCTURE.md**
- **Purpose**: This file - detailed folder structure documentation

---

### src/ Directory - Source Code

#### **__init__.py**
- Package initialization with version information

#### **config.py**
- **Purpose**: Configuration and constants
- **Contains**:
  - `DATASETS`: Dictionary mapping dataset names to IDs
  - `DATA_GOV_API_KEY`: API authentication
  - `CACHE_DIR`: Cache directory path
  - `LLM_CONFIG`: LLM integration settings (optional)

#### **data_integration.py**
- **Purpose**: Data fetching and normalization layer
- **Key Classes**:
  - `DataGovIntegrator`: Main data fetching class
    - `fetch_crop_production()`: Fetches agriculture data
    - `fetch_rainfall_data()`: Fetches climate data
    - `auto_detect_columns()`: Auto-maps dataset columns
    - `fetch_with_retry()`: Robust API calling with retry logic
  - `SyntheticDataGenerator`: Demo data generator
    - `generate_crop_production_data()`: Creates synthetic crop data
    - `generate_rainfall_data()`: Creates synthetic climate data
- **Key Features**:
  - 51+ state name normalizations
  - Smart column detection and mapping
  - Caching system with hash-based keys
  - Retry logic for API reliability

#### **query_engine.py**
- **Purpose**: Query parsing and data processing
- **Key Classes**:
  - `QueryRouter`: Parses natural language queries
    - `parse_query()`: Extracts entities and determines query type
    - Pattern-based and optional LLM routing
  - `DataProcessor`: Processes different query types
    - `process_rainfall_comparison()`: Handles rainfall comparisons
    - `process_district_ranking()`: Handles district rankings
    - `process_trend_analysis()`: Handles trend analysis
    - `process_policy_support()`: Handles policy questions
    - `format_response()`: Generates markdown responses with citations
- **Query Types**: rainfall_comparison, district_ranking, trend_analysis, policy_support

#### **data_discovery.py**
- **Purpose**: Dataset exploration and schema analysis
- **Key Classes**:
  - `DataGovExplorer`: Search and discover datasets
  - `DataStructureAnalyzer`: Analyze dataset schemas
- **Features**:
  - Dataset search functionality
  - Schema analysis and comparison
  - Unified schema creation

---

### tests/ Directory - Test Suite

#### **__init__.py**
- Package initialization for test modules

#### **test_system.py**
- **Purpose**: Complete system integration test
- **Tests**:
  - Data loading (synthetic and API)
  - Query parsing for all 4 sample questions
  - Response generation with citations
  - End-to-end flow validation
- **Usage**: `python tests/test_system.py`

#### **test_multi_question.py**
- **Purpose**: Multi-turn conversation capability test
- **Tests**:
  - 5 sequential questions
  - Different query types
  - Citation tracking across questions
  - Conversation state management
- **Usage**: `python tests/test_multi_question.py`

---

### demos/ Directory - Demonstrations

#### **__init__.py**
- Package initialization for demo scripts

#### **demo_integration_challenges.py**
- **Purpose**: Visual demonstration of data integration challenges
- **Demonstrates**:
  1. Different column structures (auto-detection solution)
  2. Inconsistent state names (51+ normalization mappings)
  3. Temporal alignment issues (year matching logic)
  4. Granularity differences (aggregation handling)
  5. Data quality issues (validation and cleaning)
- **Usage**: `python demos/demo_integration_challenges.py`

---

### docs/ Directory - Documentation

#### **PHASE1_IMPLEMENTATION.md**
- **Purpose**: Detailed Phase 1 implementation report
- **Contents**: 5 data integration challenges with solutions and code examples

#### **PHASE2_IMPLEMENTATION.md**
- **Purpose**: Phase 2 Q&A system implementation report
- **Contents**: Query routing, processing, citation system, and UI design

#### **MULTI_TURN_FEATURES.md**
- **Purpose**: Multi-turn chat capability documentation
- **Contents**: Session state management, conversation history, and chat features

#### **VIDEO_DEMO_SCRIPT.md**
- **Purpose**: Complete video demonstration script
- **Contents**: Step-by-step recording guide with all 4 sample questions

#### **FINAL_VIDEO_GUIDE.md**
- **Purpose**: 2-minute video structure guide
- **Contents**: Timestamps, talking points, and key demonstrations

---

### data_cache/ Directory

- **Purpose**: Offline operation and performance optimization
- **Structure**: Hash-based cache files (JSON format)
- **Naming**: MD5 hash of API URL for unique identification
- **Auto-created**: Directory created automatically on first data fetch

---

## Import Structure

### From Root (app.py)
```python
from src.data_integration import DataGovIntegrator, SyntheticDataGenerator
from src.query_engine import QueryRouter, DataProcessor
from src import config
```

### From tests/ and demos/
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_integration import DataGovIntegrator, SyntheticDataGenerator
from src.query_engine import QueryRouter, DataProcessor
from src import config
```

---

## Running the Project

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run the Web Interface
```powershell
streamlit run app.py
```

### 3. Run Tests
```powershell
python tests/test_system.py
python tests/test_multi_question.py
```

### 4. Run Demos
```powershell
python demos/demo_integration_challenges.py
```

---

## Key Design Decisions

### Folder Organization
- **src/**: All reusable source code (data integration, query engine, config)
- **tests/**: All test scripts for validation
- **demos/**: Standalone demonstration scripts
- **docs/**: Complete documentation for both phases
- **Root**: Entry point (app.py) and configuration (requirements.txt, README.md)

### Module Separation
- **data_integration.py**: Purely data layer - no query logic
- **query_engine.py**: Purely query/processing logic - no data fetching
- **config.py**: Centralized configuration - no business logic
- **app.py**: UI layer only - delegates to src modules

### Path Management
- Tests and demos use `sys.path` manipulation for clean imports
- Package `__init__.py` files enable proper module structure
- Root-level app.py imports directly from `src.*`

---

## Architecture Flow

```
User Question (app.py)
    ↓
Query Router (src/query_engine.py)
    ↓
Data Processor (src/query_engine.py)
    ↓
Data Integration (src/data_integration.py)
    ↓
data.gov.in API / Cache (data_cache/)
    ↓
Response with Citations (app.py)
    ↓
Multi-turn Chat Interface (app.py)
```

---

## File Count Summary

- **Python Source Files**: 5 (in src/)
- **Test Files**: 2 (in tests/)
- **Demo Files**: 1 (in demos/)
- **Documentation Files**: 6 (in docs/ + root)
- **Configuration Files**: 2 (requirements.txt, config.py)
- **Total Code Files**: 16

---

## Next Steps

1. ✅ Folder structure organized
2. ✅ Imports updated for all files
3. ✅ Package structure with `__init__.py` files
4. 🎯 **Ready for video demonstration**
5. 🎯 **Ready for deployment**

---

**Project Status**: Complete and production-ready with organized structure!
