# Project Samarth - Video Demo Script

## 2-Minute Loom Video Guide

### Introduction (15 seconds)
"Hi! I'm demonstrating Project Samarth - an intelligent multi-turn Q&A chat system that queries data.gov.in to answer complex questions about India's agricultural economy and climate patterns. You can ask unlimited questions in sequence, and the system maintains full conversation history."

---

### System Overview (30 seconds)

**Show the Streamlit interface and explain:**

"The system has 4 key components:

1. **Data Integration Layer** - Fetches and normalizes data from data.gov.in
   - Ministry of Agriculture crop production datasets
   - IMD climate/rainfall datasets
   - Smart caching for performance

2. **Query Router** - Parses natural language questions
   - Extracts entities (states, crops, years)
   - Determines which datasets to query
   - Classifies analysis type

3. **Data Processing Engine** - Synthesizes multi-source data
   - Aggregation and statistics
   - Cross-domain correlation
   - Trend analysis

4. **Citation System** - Ensures traceability
   - Every claim cites its source
   - Dataset IDs tracked
   - Full transparency"

---

### Live Demo (60 seconds)

**Demonstrate Multi-Turn Chat - Ask questions sequentially:**

**Question 1: Rainfall Comparison**
"Compare the average annual rainfall in Punjab and Haryana for the last 5 years and list the top 3 crops in each state."

*Show output, then immediately ask Question 2:*

**Question 2: District Ranking**
"Now identify the district in Punjab with the highest production of Rice and compare with the lowest in Haryana."

*Show the chat history building up, then ask Question 3:*

**Question 3: Follow-up Question**
"What is the average rainfall in Maharashtra?"

*Highlight:*
- Chat history showing all 3 questions
- Question counter incrementing
- Each answer fully cited
- Ability to clear chat and start fresh

**Key Point:** "Notice how the system handles multiple questions seamlessly - this is a true chat interface, not just a single query system!"

---

### Architecture Deep Dive (15 seconds)

**Show code structure briefly:**

```
Project Samarth/
├── app.py                 # Streamlit interface
├── data_integration.py    # API & caching
├── query_engine.py        # Query parsing & processing
├── config.py              # Dataset configurations
└── README.md              # Full documentation
```

"Built with modularity - easy to add new datasets or query types."

---

### Key Design Decisions (20 seconds)

"**Why these choices?**

1. **Multi-Turn Chat** - True conversational interface for exploring data
2. **Session State Management** - Maintains context across questions
3. **Synthetic Data Fallback** - Ensures demo works even if API is down
4. **Smart Caching** - Reduces API calls, improves performance
5. **Pattern-based Parsing** - Works without external LLM calls (data sovereignty)
6. **Extensible Architecture** - Can add GPT-4/Claude or local LLMs easily

**Core Values:**
✓ Accuracy - All claims verified
✓ Traceability - Full citation chain
✓ Data Sovereignty - Can run 100% offline
✓ Multi-turn Capability - Unlimited sequential questions"

---

### Closing (10 seconds)

"This is a fully functional end-to-end prototype that demonstrates:
- Real-time data integration
- Intelligent query routing
- Multi-source synthesis
- Complete traceability

The system is ready to answer complex policy questions with accurate, cited data. Thank you!"

---

## Key Points to Emphasize

### 1. Problem Solving & Initiative
- Identified data.gov.in API structure independently
- Built flexible system for inconsistent data formats
- Created fallback mechanisms for robustness

### 2. System Architecture
- Clean separation of concerns
- Modular, extensible design
- Smart caching and performance optimization
- Can integrate with LLMs or work standalone

### 3. Accuracy & Traceability
- Every answer includes source citations
- Dataset IDs tracked throughout
- Clear methodology for all calculations
- Transparent processing logic

### 4. Core Values
- **Data Sovereignty:** Can run fully offline
- **Privacy:** No mandatory external API calls
- **Accuracy:** Low-temperature factual responses
- **Traceability:** Complete citation chain

---

## Demo Checklist

✅ System running at http://localhost:8501
✅ All 4 sample questions tested
✅ Citations visible for all claims
✅ Code structure explained
✅ Architecture diagram shown
✅ Design decisions justified
✅ README documentation complete

---

## Technical Highlights for Video

1. **Live API Integration** (or synthetic data with explanation)
2. **Real-time Query Processing** - show the spinner and results
3. **Source Citations** - expand to show dataset IDs
4. **Multi-state Comparison** - demonstrate cross-domain synthesis
5. **Trend Analysis** - show correlation logic
6. **Policy Arguments** - demonstrate intelligent synthesis

---

## Backup Talking Points

If time permits, mention:
- Can extend to use GPT-4, Claude, or Llama for better NLU
- Can add more ministries/datasets easily
- Architecture supports GraphQL/REST API layer
- Can add visualization (charts, maps)
- Multilingual support possible (Hindi, etc.)

---

## Recording Tips

1. **Keep it fast-paced** - 2 minutes goes quickly
2. **Show, don't just tell** - demonstrate features live
3. **Highlight citations** - this is a key differentiator
4. **Show code briefly** - but focus on the working system
5. **End strong** - emphasize it's a complete, working prototype

---

## Application Access

**Local URL:** http://localhost:8501
**To restart if needed:**
```powershell
cd "c:\Users\hp\Desktop\Project Samarth"
& "C:\Users\hp\AppData\Local\Programs\Python\Python313\python.exe" -m streamlit run app.py
```

---

## Questions It Can Answer

✓ Comparative analysis across states
✓ District-level rankings
✓ Temporal trends over years
✓ Climate-agriculture correlation
✓ Policy support with data backing
✓ Top N queries (top M crops, etc.)
✓ Year-over-year changes
✓ Multi-source data synthesis

**All with complete source attribution!**
