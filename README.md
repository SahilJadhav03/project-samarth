# Project Samarth 🌾

## Intelligent Q&A System for Agricultural & Climate Data

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Data.gov.in](https://img.shields.io/badge/Data-data.gov.in-00A36C?style=for-the-badge)](https://data.gov.in/)

🔗 **[Live Demo](https://project-samarth.streamlit.app/)** | 📹 **[Video Demo](#)** | 📊 **[GitHub](https://github.com/SahilJadhav03/project-samarth)**

An end-to-end prototype that queries **data.gov.in** to answer complex, natural language questions about India's agricultural economy and climate patterns.

---

## 🎯 Project Overview

**Vision:** Government portals like data.gov.in contain valuable datasets, but they exist in varied formats across ministries. Project Samarth solves this by providing an intelligent system that:

- Sources data directly from data.gov.in
- Handles inconsistent data structures
- Synthesizes cross-domain insights
- Provides accurate, traceable answers

---

## ✨ Key Features

### 1. **Multi-Turn Chat Interface** 🆕
- Ask unlimited sequential questions
- Maintains conversation history
- Context-aware across questions
- Clear chat history option
- Question counter and tracking

### 2. **Multi-Source Data Integration**
- Fetches data from Ministry of Agriculture & Farmers Welfare
- Integrates IMD (India Meteorological Department) climate data
- Handles different formats (CSV, JSON, Excel)
- Smart caching for performance

### 3. **Intelligent Query Routing**
- Parses natural language questions
- Identifies required data sources
- Determines analysis type (aggregation, correlation, ranking)
- Extensible to use LLMs (GPT-4, Claude, or local models)

### 4. **Cross-Domain Synthesis**
- Correlates agricultural production with climate patterns
- Performs trend analysis over time
- Generates policy-support arguments
- Handles district, state, and national-level queries

### 5. **Source Citation & Traceability**
- Every data point is cited with source
- Dataset IDs are tracked
- Transparent data provenance

### 6. **User-Friendly Interface**
- Clean Streamlit web interface
- Sample questions for quick testing
- Real-time analysis
- Visual data presentation
- Chat history display

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                  (Streamlit Web App)                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Query Router                            │
│        (Natural Language Understanding)                  │
│   • Parse intent                                         │
│   • Extract entities (states, crops, years)              │
│   • Determine data sources needed                        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Data Integration Layer                      │
│                                                           │
│  ┌─────────────────┐         ┌─────────────────┐       │
│  │ Agriculture Data│         │  Climate Data   │       │
│  │  (Crop Prod.)   │         │   (Rainfall)    │       │
│  └────────┬────────┘         └────────┬────────┘       │
│           │                            │                 │
│           └────────────┬───────────────┘                │
│                        │                                 │
│                   data.gov.in API                        │
│                        │                                 │
│                   Smart Cache                            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Data Processing Engine                      │
│   • Normalize data structures                            │
│   • Aggregate & compute statistics                       │
│   • Correlate across datasets                            │
│   • Generate insights                                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Response Generator                          │
│   • Format human-readable answers                        │
│   • Attach source citations                              │
│   • Structure data for presentation                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection (for data.gov.in API)

### Installation

1. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

2. **Run the application:**
```powershell
streamlit run app.py
```

3. **Access the interface:**
Open your browser to `http://localhost:8501`

---

## 📊 Sample Questions

The system can answer questions like:

### 1. **Comparative Analysis**
> *"Compare the average annual rainfall in Punjab and Haryana for the last 5 available years. In parallel, list the top 3 most produced crops in each of those states during the same period."*

### 2. **District-Level Rankings**
> *"Identify the district in Punjab with the highest production of Rice in the most recent year available and compare that with the district with the lowest production of Rice in Haryana."*

### 3. **Trend & Correlation Analysis**
> *"Analyze the production trend of Rice in Punjab over the last decade. Correlate this trend with the corresponding climate data for the same period."*

### 4. **Policy Support**
> *"A policy advisor is proposing a scheme to promote drought-resistant crops over water-intensive crops in Maharashtra. Based on historical data from the last 5 years, what are the three most compelling data-backed arguments to support this policy?"*

---

## 🗂️ Project Structure

```
Project Samarth/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration & dataset IDs
├── data_integration.py       # Data fetching & normalization
├── query_engine.py           # Query parsing & processing
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── data_cache/              # Cached datasets (auto-created)
```

---

## 🔧 Technical Design Decisions

### 1. **Data Integration Strategy**
- **Challenge:** data.gov.in datasets have inconsistent structures
- **Solution:** 
  - Built flexible data fetching layer
  - Normalize state names and data formats
  - Smart caching to reduce API calls
  - Fallback to synthetic data for demos

### 2. **Query Understanding**
- **Challenge:** Parse complex natural language queries
- **Solution:**
  - Pattern-based parsing for common query types
  - Entity extraction (states, crops, years, values)
  - Extensible to LLM-based parsing
  - Query intent classification

### 3. **Cross-Domain Synthesis**
- **Challenge:** Combine agriculture and climate data
- **Solution:**
  - Temporal alignment (match years)
  - Geographic alignment (match states/districts)
  - Statistical correlation
  - Clear methodology for each analysis type

### 4. **Data Sovereignty**
- **Challenge:** Ensure privacy and security
- **Solution:**
  - Can run entirely offline with cached data
  - No external LLM calls in default mode
  - Local data processing
  - Extensible to use local LLMs (Llama, Mistral)

### 5. **Accuracy & Traceability**
- **Challenge:** Ensure trustworthy answers
- **Solution:**
  - Every claim cites source dataset
  - Dataset IDs tracked throughout
  - Source metadata preserved
  - Transparent processing logic

---

## 🎥 Video Demonstration

The system demonstrates:
1. **Data Discovery:** How we identified and accessed data.gov.in datasets
2. **Architecture:** Multi-layer design with clear separation of concerns
3. **Query Processing:** End-to-end flow from question to answer
4. **Citation System:** How every data point is traceable
5. **Live Demo:** Answering all 4 sample questions

---

## 🌟 Key Capabilities

✅ **Multi-turn chat interface** - Ask unlimited questions sequentially  
✅ **Conversation history** - Track all questions and answers  
✅ **Real-time data fetching** from data.gov.in  
✅ **Multi-dataset synthesis** (agriculture + climate)  
✅ **Complex query handling** (comparison, trends, policy support)  
✅ **Source citation** for every claim  
✅ **Smart caching** for performance  
✅ **Fallback synthetic data** for demos  
✅ **Clean web interface** for easy interaction  
✅ **Extensible architecture** for additional data sources  

---

## 🔮 Future Enhancements

1. **LLM Integration:** Add GPT-4/Claude for better query understanding
2. **More Data Sources:** Expand to water resources, soil data, etc.
3. **Visualization:** Add charts and graphs for trends
4. **Advanced Analytics:** ML models for predictions
5. **API Mode:** RESTful API for programmatic access
6. **Multi-language:** Support Hindi and other Indian languages

---

## 📝 Core Values Addressed

### ✅ Accuracy & Traceability
- Every answer cites specific datasets
- Source metadata preserved throughout
- Clear calculation methodology

### ✅ Data Sovereignty & Privacy
- Can run fully offline
- Local data processing
- No mandatory external API calls
- Extensible to local LLMs

### ✅ Robustness
- Handles API failures gracefully
- Smart caching prevents repeated calls
- Data normalization handles inconsistencies
- Clear error handling

---

## 👨‍💻 Developer Notes

### Adding New Datasets

1. Add dataset ID to `config.py`:
```python
DATASETS = {
    "your_dataset": {
        "id": "dataset-id-from-data-gov-in",
        "name": "Dataset Name",
        "ministry": "Ministry Name"
    }
}
```

2. Create fetch method in `data_integration.py`:
```python
def fetch_your_data(self, filters):
    return self.fetch_dataset("your_dataset_id", filters)
```

3. Add processing logic in `query_engine.py`

### Extending Query Types

Add new query type in `QueryRouter.parse_query()` and corresponding processor in `DataProcessor`

---

## 📄 License

This project is built for the Samarth challenge submission.

---

## 🙏 Acknowledgments

- **data.gov.in** for providing open government data
- **Ministry of Agriculture & Farmers Welfare** for crop production datasets
- **India Meteorological Department (IMD)** for climate data
- **Streamlit** for the excellent web framework

---

**Built with ❤️ for better data-driven policy making in India**
