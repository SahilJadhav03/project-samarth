"""
Query Router and Processing Engine for Project Samarth
Uses LLM to understand questions and route to appropriate data sources
"""

import pandas as pd
import json
import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryIntent:
    """Represents the parsed intent of a user query"""
    query_type: str  # comparison, trend_analysis, policy_support, district_ranking
    entities: Dict[str, Any]  # states, crops, years, etc.
    data_sources_needed: List[str]  # crop_production, rainfall
    analysis_type: str  # aggregation, correlation, ranking


class QueryRouter:
    """
    Routes user queries to appropriate data sources and processing logic
    """
    
    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        
    def parse_query(self, query: str) -> QueryIntent:
        """
        Parse user query to understand intent and extract entities
        
        For demo purposes, uses pattern matching. 
        In production, would use LLM (GPT-4, Claude, or local model)
        """
        
        query_lower = query.lower()
        
        # Extract entities
        entities = self._extract_entities(query)
        analysis_hint = entities.get("analysis")
        
        # Determine query type based on keywords (order matters - most specific first)
        if (
            "policy" in query_lower
            or "should we" in query_lower
            or "recommend" in query_lower
            or "strategy" in query_lower
            or "plan" in query_lower
            or "promote" in query_lower
        ):
            query_type = "policy_support"
            data_sources = ["crop_production", "rainfall"]
            analysis_type = "synthesis"
        elif "compare" in query_lower and "rain" in query_lower:
            query_type = "rainfall_comparison"
            data_sources = ["rainfall", "crop_production"]
            analysis_type = "aggregation"
        elif "correlate" in query_lower or "impact" in query_lower or "relationship" in query_lower:
            query_type = "correlation_query"
            data_sources = ["crop_production", "rainfall"]
            analysis_type = "correlation"
        elif any(keyword in query_lower for keyword in ["highest", "lowest", "top", "rank", "most", "least"]):
            if "district" in query_lower or "districts" in query_lower:
                query_type = "district_ranking"
                data_sources = ["crop_production"]
                analysis_type = "ranking"
            else:
                query_type = "state_ranking"
                data_sources = ["crop_production"]
                analysis_type = "ranking"
        elif (
            "trend" in query_lower
            or "over the last decade" in query_lower
            or analysis_hint == "trend"
        ):
            query_type = "trend_analysis"
            data_sources = ["crop_production", "rainfall"]
            analysis_type = "correlation"
        elif "compare" in query_lower or "versus" in query_lower or "vs" in query_lower:
            query_type = "production_comparison"
            data_sources = ["crop_production"]
            analysis_type = "comparison"
        elif (
            "rainfall" in query_lower
            or "rain" in query_lower
            or "precipitation" in query_lower
        ) and not any(
            crop in query_lower for crop in [
                "wheat",
                "rice",
                "cotton",
                "sugarcane",
                "bajra",
                "jowar",
                "maize",
            ]
        ):
            # Pure rainfall query (no crop mentioned)
            query_type = "rainfall_query"
            data_sources = ["rainfall"]
            analysis_type = "aggregation"
        elif "average" in query_lower or "mean" in query_lower or "typical" in query_lower:
            query_type = "production_query"
            data_sources = ["crop_production"]
            analysis_type = "aggregation"
        elif not entities.get("states") and not entities.get("crops") and not entities.get("years"):
            query_type = "clarification"
            data_sources = []
            analysis_type = "guidance"
        else:
            # Default to simple production query if no clear pattern
            query_type = "production_query"
            data_sources = ["crop_production"]
            analysis_type = "aggregation"
        
        return QueryIntent(
            query_type=query_type,
            entities=entities,
            data_sources_needed=data_sources,
            analysis_type=analysis_type
        )
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """
        Extract entities like states, crops, years from query
        """
        entities = {
            "states": [],
            "districts": [],
            "crops": [],
            "years": [],
            "n_value": None,
            "m_value": None,
            "crop_type": None,
            "analysis": None,
            "ranking_focus": None
        }
        
        query_lower = query.lower()
        
        # Common Indian states (expandable list)
        states = [
            "Punjab", "Haryana", "Uttar Pradesh", "Maharashtra", "Karnataka",
            "Tamil Nadu", "Andhra Pradesh", "Telangana", "West Bengal", "Bihar",
            "Rajasthan", "Madhya Pradesh", "Gujarat", "Odisha", "Kerala",
            "Chhattisgarh", "Jharkhand", "Assam", "Himachal Pradesh", "Uttarakhand"
        ]
        
        for state in states:
            if state.lower() in query_lower:
                entities["states"].append(state)
        
        # Extract district names using stricter patterns to avoid capturing generic phrases
        district_pattern = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+districts?\b")
        noise_prefixes = {"Identify", "Which", "What", "Compare", "List", "Top", "Lowest", "Highest", "Best"}
        for match in district_pattern.finditer(query):
            candidate = match.group(1).strip()
            if not candidate:
                continue
            first_word = candidate.split()[0]
            if first_word in noise_prefixes:
                continue
            if len(candidate.split()) > 3:
                continue
            if candidate not in entities["districts"]:
                entities["districts"].append(candidate)
        
        # Extract years
        year_pattern = r'\b(20\d{2}|19\d{2})\b'
        years = re.findall(year_pattern, query)
        entities["years"] = years
        
        # Detect phrases like "last year", "past decade"
        relative_time_phrases = {
            "last year": 1,
            "past year": 1,
            "previous year": 1,
            "last two years": 2,
            "past two years": 2,
            "last 5 years": 5,
            "past 5 years": 5,
            "last five years": 5,
            "last decade": 10,
            "past decade": 10
        }
        for phrase, value in relative_time_phrases.items():
            if phrase in query_lower:
                entities["n_value"] = value
                break
        
        # Extract N and M values
        n_match = re.search(r'last (\d+) (?:available )?years?', query, re.IGNORECASE)
        if n_match:
            entities["n_value"] = int(n_match.group(1))
        
        m_match = re.search(r'top (\d+)', query, re.IGNORECASE)
        if m_match:
            entities["m_value"] = int(m_match.group(1))
        
        # Extract crops and handle category keywords
        crops = [
            "Rice", "Wheat", "Sugarcane", "Cotton", "Jowar", "Bajra", "Maize",
            "Tur", "Gram", "Groundnut", "Soybean", "Sunflower", "Potato", "Onion",
            "Millet", "Paddy"
        ]
        
        crop_synonyms = {
            "millets": ["Bajra", "Jowar"],
            "pulses": ["Tur", "Gram"],
            "oilseeds": ["Groundnut", "Soybean", "Sunflower"],
            "coarse cereals": ["Jowar", "Bajra", "Maize"],
        }
        
        for crop in crops:
            if crop.lower() in query_lower:
                entities["crops"].append(crop if crop != "Paddy" else "Rice")
        
        for synonym, mapped_crops in crop_synonyms.items():
            if synonym in query_lower:
                entities["crops"].extend(mapped_crops)
        
        # Deduplicate lists while preserving order
        entities["states"] = list(dict.fromkeys(entities["states"]))
        entities["districts"] = list(dict.fromkeys(entities["districts"]))
        entities["crops"] = list(dict.fromkeys(entities["crops"]))
        
        # Detect crop types
        if "drought-resistant" in query_lower or "drought resistant" in query_lower:
            entities["crop_type"] = "drought-resistant"
        elif "water-intensive" in query_lower or "water intensive" in query_lower:
            entities["crop_type"] = "water-intensive"
        
        # Detect analytical intent keywords
        if any(word in query_lower for word in ["trend", "trajectory", "pattern"]):
            entities["analysis"] = "trend"
        elif any(word in query_lower for word in ["compare", "versus", "vs"]):
            entities["analysis"] = "comparison"
        elif any(word in query_lower for word in ["support", "recommend", "should we"]):
            entities["analysis"] = "policy"
        
        if any(word in query_lower for word in ["highest", "top", "leading", "best"]):
            entities["ranking_focus"] = "highest"
        elif any(word in query_lower for word in ["lowest", "bottom", "least", "lagging"]):
            entities["ranking_focus"] = "lowest"
        
        return entities


class DataProcessor:
    """
    Processes and synthesizes data from multiple sources
    """
    
    def __init__(self):
        self.citations = []
    
    def process_rainfall_comparison(self, rainfall_df: pd.DataFrame, 
                                   crop_df: pd.DataFrame,
                                   intent: QueryIntent) -> Dict[str, Any]:
        """
        Process queries comparing rainfall across states
        """
        result = {
            "type": "rainfall_comparison",
            "data": {},
            "citations": []
        }
        
        states = intent.entities.get("states", [])
        n_years = intent.entities.get("n_value")
        if not isinstance(n_years, int) or n_years <= 0:
            n_years = 5
        m_crops = intent.entities.get("m_value")
        if not isinstance(m_crops, int) or m_crops <= 0:
            m_crops = 3
        
        # Get recent years
        if not rainfall_df.empty and "year" in rainfall_df.columns:
            years = sorted(rainfall_df["year"].unique(), reverse=True)[:n_years]
        else:
            years = [str(y) for y in range(2019, 2024)]
        
        # Calculate average rainfall for each state
        for state in states:
            state_data = {}
            
            # Rainfall analysis
            state_rainfall = rainfall_df[
                (rainfall_df["state"] == state) & 
                (rainfall_df["year"].isin([str(y) for y in years]))
            ]
            
            if not state_rainfall.empty:
                avg_rainfall = state_rainfall["annual_rainfall"].mean()
                state_data["avg_rainfall"] = round(avg_rainfall, 2)
                state_data["years_analyzed"] = years
                
                result["citations"].append({
                    "claim": f"Average annual rainfall in {state}",
                    "source": state_rainfall["_source"].iloc[0] if "_source" in state_rainfall.columns else "data.gov.in",
                    "dataset_id": state_rainfall["_dataset_id"].iloc[0] if "_dataset_id" in state_rainfall.columns else "N/A"
                })
            
            # Top crops by production
            state_crops = crop_df[
                (crop_df["state_name"] == state) & 
                (crop_df["crop_year"].isin([str(y) for y in years]))
            ]
            
            if not state_crops.empty:
                top_crops = (state_crops.groupby("crop")["production"]
                           .sum()
                           .sort_values(ascending=False)
                           .head(m_crops))
                
                state_data["top_crops"] = [
                    {"crop": crop, "total_production": round(prod, 2)}
                    for crop, prod in top_crops.items()
                ]
                
                result["citations"].append({
                    "claim": f"Top {m_crops} crops in {state}",
                    "source": state_crops["_source"].iloc[0] if "_source" in state_crops.columns else "data.gov.in",
                    "dataset_id": state_crops["_dataset_id"].iloc[0] if "_dataset_id" in state_crops.columns else "N/A"
                })
            
            result["data"][state] = state_data
        
        return result
    
    def process_district_ranking(self, crop_df: pd.DataFrame, 
                                intent: QueryIntent) -> Dict[str, Any]:
        """
        Process queries about district-level crop production rankings
        """
        result = {
            "type": "district_ranking",
            "data": {},
            "citations": []
        }
        
        crops = intent.entities.get("crops", []) or ["Rice"]
        crop = crops[0]
        focus = intent.entities.get("ranking_focus", "highest")
        top_n = intent.entities.get("m_value")
        if not isinstance(top_n, int) or top_n <= 0:
            top_n = 3
        states = intent.entities.get("states", [])
        
        # Derive candidate states if none provided
        if not states and not crop_df.empty:
            state_totals = (
                crop_df[crop_df["crop"] == crop]
                .groupby("state_name")["production"]
                .sum()
                .sort_values(ascending=False)
            )
            if not state_totals.empty:
                states = state_totals.head(3).index.tolist()
                result["data"]["note"] = f"Showing {focus} districts in top {len(states)} producing states for {crop}."
        
        if not states:
            result["data"]["message"] = "Unable to identify relevant states for district ranking. Try specifying a state name."
            return result
        
        # Determine most recent year available
        if not crop_df.empty and "crop_year" in crop_df.columns:
            recent_year = str(max(crop_df["crop_year"].astype(int)))
        else:
            recent_year = "2023"
        
        for state in states:
            state_crop_data = crop_df[
                (crop_df["state_name"] == state)
                & (crop_df["crop"] == crop)
                & (crop_df["crop_year"] == recent_year)
            ]
            
            if state_crop_data.empty:
                result["data"][state] = {
                    "state": state,
                    "crop": crop,
                    "year": recent_year,
                    "message": f"No district-level data available for {crop}."
                }
                continue
            
            district_production = (
                state_crop_data.groupby("district_name")["production"].sum()
                .sort_values(ascending=False)
            )
            
            if district_production.empty:
                result["data"][state] = {
                    "state": state,
                    "crop": crop,
                    "year": recent_year,
                    "message": "District production data missing."
                }
                continue
            
            if focus == "lowest":
                selected = district_production.tail(top_n)
            else:
                selected = district_production.head(top_n)
            
            result["data"][state] = {
                "state": state,
                "crop": crop,
                "year": recent_year,
                "focus": focus,
                "districts": [
                    {"district": dist, "production": round(value, 2)}
                    for dist, value in selected.items()
                ]
            }
            
            result["citations"].append({
                "claim": f"District-level {crop} production in {state} for {recent_year}",
                "source": state_crop_data["_source"].iloc[0] if "_source" in state_crop_data.columns else "data.gov.in",
                "dataset_id": state_crop_data["_dataset_id"].iloc[0] if "_dataset_id" in state_crop_data.columns else "N/A"
            })
        
        return result

    def process_state_ranking(self, crop_df: pd.DataFrame,
                              intent: QueryIntent) -> Dict[str, Any]:
        """Process queries about state-level crop production rankings."""
        result = {
            "type": "state_ranking",
            "data": {},
            "citations": []
        }
        
        crops = intent.entities.get("crops", []) or ["Rice"]
        crop = crops[0]
        focus = intent.entities.get("ranking_focus", "highest")
        top_n = intent.entities.get("m_value")
        if not isinstance(top_n, int) or top_n <= 0:
            top_n = 5
        states_filter = intent.entities.get("states", [])
        years_filter = intent.entities.get("years", [])
        n_years = intent.entities.get("n_value")
        if not isinstance(n_years, int) or n_years <= 0:
            n_years = 5
        
        if crop_df.empty:
            result["data"]["message"] = "Crop production dataset is empty."
            return result
        
        df = crop_df[crop_df["crop"] == crop].copy()
        if df.empty:
            available_crops = sorted(crop_df["crop"].dropna().unique().tolist())
            result["data"]["message"] = (
                f"No production data found for {crop}. Available crops: {', '.join(available_crops[:10])}."
            )
            return result
        
        if states_filter:
            df = df[df["state_name"].isin(states_filter)]
            if df.empty:
                result["data"]["message"] = (
                    "Specified states do not have data for this crop. Try removing the state filter."
                )
                return result
        
        # Normalize crop_year for filtering
        df["crop_year"] = df["crop_year"].astype(str)
        if years_filter:
            target_years = years_filter
        else:
            unique_years = sorted(df["crop_year"].unique(), reverse=True)
            target_years = unique_years[:n_years]
        
        df = df[df["crop_year"].isin(target_years)]
        if df.empty:
            result["data"]["message"] = "No data available for the selected years."
            return result
        
        state_totals = (
            df.groupby("state_name")["production"]
            .sum()
            .sort_values(ascending=(focus == "lowest"))
        )
        
        selected_states = state_totals.head(top_n)
        if selected_states.empty:
            result["data"]["message"] = "Unable to compute rankings due to insufficient data."
            return result
        
        result["data"] = {
            "crop": crop,
            "focus": focus,
            "years_considered": target_years,
            "states": [
                {"state": state, "total_production": round(total, 2)}
                for state, total in selected_states.items()
            ],
        }
        
        citation_source = df["_source"].iloc[0] if "_source" in df.columns else "data.gov.in"
        citation_dataset = df["_dataset_id"].iloc[0] if "_dataset_id" in df.columns else "N/A"
        result["citations"].append({
            "claim": f"State-level {crop} production rankings",
            "source": citation_source,
            "dataset_id": citation_dataset
        })
        
        return result
    
    def process_trend_analysis(self, crop_df: pd.DataFrame, 
                              rainfall_df: pd.DataFrame,
                              intent: QueryIntent) -> Dict[str, Any]:
        """
        Process queries analyzing trends and correlations
        """
        result = {
            "type": "trend_analysis",
            "data": {},
            "citations": []
        }
        
        states = intent.entities.get("states", [])
        crops = intent.entities.get("crops", [])
        
        if not states:
            states = crop_df["state_name"].unique()[:2].tolist() if not crop_df.empty else ["Punjab"]
        
        if not crops:
            crops = ["Rice"]
        
        crop = crops[0]
        
        # Analyze last 10 years
        current_year = 2023
        years = [str(y) for y in range(current_year - 9, current_year + 1)]
        
        for state in states:
            # Production trend
            state_crop_data = crop_df[
                (crop_df["state_name"] == state) & 
                (crop_df["crop"] == crop) &
                (crop_df["crop_year"].isin(years))
            ]
            
            if not state_crop_data.empty:
                yearly_production = (state_crop_data.groupby("crop_year")["production"]
                                   .sum()
                                   .sort_index())
                
                # Calculate trend (simple linear)
                if len(yearly_production) >= 3:
                    x = list(range(len(yearly_production)))
                    y = yearly_production.values
                    trend = "increasing" if y[-1] > y[0] else "decreasing"
                    pct_change = ((y[-1] - y[0]) / y[0] * 100) if y[0] != 0 else 0
                else:
                    trend = "insufficient_data"
                    pct_change = 0
                
                result["data"][f"{state}_production_trend"] = {
                    "state": state,
                    "crop": crop,
                    "trend": trend,
                    "percent_change": round(pct_change, 2),
                    "years_analyzed": years,
                    "yearly_data": {str(year): round(prod, 2) 
                                  for year, prod in yearly_production.items()}
                }
                
                result["citations"].append({
                    "claim": f"Production trend of {crop} in {state}",
                    "source": state_crop_data["_source"].iloc[0] if "_source" in state_crop_data.columns else "data.gov.in",
                    "dataset_id": state_crop_data["_dataset_id"].iloc[0] if "_dataset_id" in state_crop_data.columns else "N/A"
                })
            
            # Rainfall correlation
            state_rainfall = rainfall_df[
                (rainfall_df["state"] == state) & 
                (rainfall_df["year"].isin(years))
            ]
            
            if not state_rainfall.empty:
                yearly_rainfall = (state_rainfall.groupby("year")["annual_rainfall"]
                                 .mean()
                                 .sort_index())
                
                result["data"][f"{state}_rainfall_trend"] = {
                    "state": state,
                    "avg_rainfall": round(yearly_rainfall.mean(), 2),
                    "yearly_data": {str(year): round(rain, 2) 
                                  for year, rain in yearly_rainfall.items()}
                }
                
                result["citations"].append({
                    "claim": f"Rainfall data for {state}",
                    "source": state_rainfall["_source"].iloc[0] if "_source" in state_rainfall.columns else "data.gov.in",
                    "dataset_id": state_rainfall["_dataset_id"].iloc[0] if "_dataset_id" in state_rainfall.columns else "N/A"
                })
                
                # Simple correlation analysis
                if f"{state}_production_trend" in result["data"]:
                    result["data"][f"{state}_correlation"] = {
                        "observation": "Climate and production patterns suggest correlation" 
                                     if trend in yearly_rainfall else "Further analysis needed"
                    }
        
        return result
    
    def process_policy_support(self, crop_df: pd.DataFrame, 
                              rainfall_df: pd.DataFrame,
                              intent: QueryIntent) -> Dict[str, Any]:
        """
        Process queries requesting policy support arguments
        """
        result = {
            "type": "policy_support",
            "data": {},
            "citations": []
        }
        
        states = intent.entities.get("states", [])
        crop_focus = intent.entities.get("crop_type") or "drought-resistant"
        n_years = intent.entities.get("n_value")
        if not isinstance(n_years, int) or n_years <= 0:
            n_years = 5
        years = [str(y) for y in range(2023 - n_years + 1, 2024)]
        
        drought_resistant = ["Bajra", "Jowar", "Groundnut"]
        water_intensive = ["Rice", "Sugarcane"]
        focus_label = "drought-resistant crops" if "drought" in crop_focus else "water-efficient crops"
        target_crops = drought_resistant if "drought" in crop_focus else water_intensive
        alternate_crops = water_intensive if "drought" in crop_focus else drought_resistant
        
        available_states = (
            sorted(crop_df["state_name"].dropna().unique().tolist())
            if not crop_df.empty and "state_name" in crop_df.columns else []
        )
        default_state_note = None
        
        if not states:
            if available_states:
                states = [available_states[0]]
                default_state_note = f"No state specified; using {states[0]} based on available data."
            else:
                result["data"]["message"] = (
                    "Unable to find regional data to support policy recommendations. Please mention a state."
                )
                result["data"]["policy"] = {
                    "promote": crop_focus,
                    "region": "target region",
                    "period": f"{n_years} years"
                }
                return result
        
        arguments = []
        
        for state in states[:1]:
            # Argument 1: Rainfall patterns
            state_rainfall = rainfall_df[
                (rainfall_df["state"] == state)
                & (rainfall_df["year"].isin(years))
            ] if not rainfall_df.empty else pd.DataFrame()
            
            if not state_rainfall.empty:
                avg_rainfall = state_rainfall["annual_rainfall"].mean()
                rainfall_argument = {
                    "argument": 1,
                    "title": "Climate Suitability",
                    "description": (
                        f"Average annual rainfall in {state} is {round(avg_rainfall, 2)}mm "
                        f"over the last {n_years} years. This supports prioritizing {focus_label}."
                    ),
                    "data_points": [f"Avg rainfall: {round(avg_rainfall, 2)}mm"],
                    "source": state_rainfall["_source"].iloc[0] if "_source" in state_rainfall.columns else "IMD"
                }
                arguments.append(rainfall_argument)
            else:
                arguments.append({
                    "argument": 1,
                    "title": "Climate Suitability",
                    "description": (
                        f"Rainfall data for {state} is unavailable for the requested period. "
                        "Consider validating climate suitability with local IMD records."
                    ),
                    "data_points": ["Rainfall dataset unavailable"],
                    "source": "IMD (pending)"
                })
            
            # Argument 2: Production viability
            target_production = crop_df[
                (crop_df["state_name"] == state)
                & (crop_df["crop"].isin(target_crops))
                & (crop_df["crop_year"].isin(years))
            ] if not crop_df.empty else pd.DataFrame()
            
            if not target_production.empty:
                total_target = target_production["production"].sum()
                arguments.append({
                    "argument": 2,
                    "title": "Historical Production Success",
                    "description": (
                        f"{focus_label.title()} have produced {round(total_target, 2)} units in {state} "
                        f"over {n_years} years, demonstrating viability."
                    ),
                    "data_points": [f"Total production: {round(total_target, 2)}"],
                    "source": target_production["_source"].iloc[0] if "_source" in target_production.columns else "Ministry of Agriculture"
                })
            else:
                arguments.append({
                    "argument": 2,
                    "title": "Historical Production Success",
                    "description": (
                        f"Production data for {focus_label} in {state} is missing. "
                        "Encourage pilot programs to gather productivity evidence."
                    ),
                    "data_points": ["Production dataset unavailable"],
                    "source": "Ministry of Agriculture (pending)"
                })
            
            # Argument 3: Resource efficiency vs alternate crops
            alternate_production = crop_df[
                (crop_df["state_name"] == state)
                & (crop_df["crop"].isin(alternate_crops))
                & (crop_df["crop_year"].isin(years))
            ] if not crop_df.empty else pd.DataFrame()
            
            data_points = []
            if not alternate_production.empty:
                total_alternate = alternate_production["production"].sum()
                data_points.append(f"Water-intensive crop output: {round(total_alternate, 2)} units")
            
            arguments.append({
                "argument": 3,
                "title": "Resource Optimization",
                "description": (
                    f"Transitioning to {focus_label} can diversify income while easing pressure on water resources."
                ),
                "data_points": data_points or ["No alternate crop data found"],
                "source": "Cross-dataset synthesis"
            })
        
        result_data = result["data"]
        if default_state_note:
            result_data["note"] = default_state_note
        
        result_data["arguments"] = arguments
        result_data["policy"] = {
            "promote": crop_focus,
            "region": states[0] if states else "target region",
            "period": f"{n_years} years"
        }
        result_data["next_steps"] = "Validate recommendations with local extension officers and updated IMD bulletins."
        
        for arg in arguments:
            result["citations"].append({
                "claim": arg["title"],
                "source": arg.get("source", "data.gov.in"),
                "data": arg.get("data_points", [])
            })
        
        return result
    
    def process_rainfall_query(self, rainfall_df: pd.DataFrame,
                               intent: QueryIntent) -> Dict[str, Any]:
        """
        Process pure rainfall queries (e.g., "Punjab rainfall in 2023")
        """
        result = {
            "type": "rainfall_query",
            "data": {},
            "citations": []
        }
        
        states = intent.entities.get("states", [])
        years = intent.entities.get("years", [])
        
        if not states:
            states = ["Punjab"]  # Default
        
        available_rainfall_states: List[str] = []
        if not rainfall_df.empty and "state" in rainfall_df.columns:
            available_rainfall_states = sorted(
                rainfall_df["state"].dropna().unique().tolist()
            )

        # Get all available years if not specified
        if not years and not rainfall_df.empty and "year" in rainfall_df.columns:
            all_years = sorted(rainfall_df["year"].unique(), reverse=True)
            years = [str(all_years[0])]  # Most recent year
        elif not years:
            years = ["2023"]  # Default
        
        for state in states:
            state_data = {
                "state": state,
                "years": years
            }
            
            # Get rainfall data
            state_rainfall = rainfall_df[
                (rainfall_df["state"] == state) & 
                (rainfall_df["year"].isin([str(y) for y in years]))
            ]
            
            if not state_rainfall.empty:
                if len(years) == 1:
                    # Single year query
                    avg_rainfall = state_rainfall["annual_rainfall"].mean()
                    state_data["rainfall"] = round(avg_rainfall, 2)
                    state_data["year"] = years[0]
                else:
                    # Multiple years
                    year_wise = state_rainfall.groupby("year")["annual_rainfall"].mean().to_dict()
                    state_data["year_wise_rainfall"] = {str(k): round(v, 2) for k, v in year_wise.items()}
                    state_data["average_rainfall"] = round(state_rainfall["annual_rainfall"].mean(), 2)
                
                result["citations"].append({
                    "claim": f"Rainfall data for {state} ({', '.join(map(str, years))})",
                    "source": state_rainfall["_source"].iloc[0] if "_source" in state_rainfall.columns else "IMD - India Meteorological Department",
                    "dataset_id": state_rainfall["_dataset_id"].iloc[0] if "_dataset_id" in state_rainfall.columns else "rainfall_data"
                })
            else:
                hint = ""
                if available_rainfall_states:
                    preview_states = ", ".join(available_rainfall_states[:5])
                    if len(available_rainfall_states) > 5:
                        preview_states += ", ..."
                    hint = f" Available states in this demo: {preview_states}."
                state_data["message"] = (
                    f"No rainfall readings for {state} across {', '.join(map(str, years))} in the current dataset." + hint
                )
            
            result["data"][state] = state_data
        
        return result
    
    def process_production_query(self, crop_df: pd.DataFrame, 
                                 rainfall_df: pd.DataFrame,
                                 intent: QueryIntent) -> Dict[str, Any]:
        """
        Process simple production queries (e.g., "What is the average Wheat production in Karnataka?")
        """
        result = {
            "type": "production_query",
            "data": {},
            "citations": []
        }
        
        guidance_suggestions = [
            "Show wheat production in Punjab over the last 5 years",
            "Compare rice output between Maharashtra and Karnataka",
            "List top districts for cotton production in Telangana"
        ]

        requested_crops = intent.entities.get("crops", [])
        n_years = intent.entities.get("n_value")
        if not isinstance(n_years, int) or n_years <= 0:
            n_years = 3  # Default to 3 years

        crops = requested_crops[:] if requested_crops else []
        if not crops:
            crops = ["Wheat"]  # Default crop

        crop = crops[0]
        requested_crop = requested_crops[0] if requested_crops else None

        available_states_for_crop: List[str] = []
        if not crop_df.empty and "state_name" in crop_df.columns:
            available_states_for_crop = sorted(
                crop_df.loc[crop_df["crop"] == crop, "state_name"]
                .dropna()
                .unique()
                .tolist()
            )

        states = intent.entities.get("states", [])
        if not states and not crop_df.empty:
            state_production = crop_df[crop_df["crop"] == crop].groupby("state_name")["production"].sum()
            if not state_production.empty:
                top_state = state_production.idxmax()
                states = [top_state]
                result["data"]["note"] = f"Showing data for {top_state} (highest {crop} producer)"

        if not states:
            if requested_crop:
                result["data"]["message"] = (
                    f"I couldn't find production records for {requested_crop}. "
                    "Try mentioning a state along with the crop or choose a different crop available in the dataset."
                )
            else:
                result["data"]["message"] = (
                    "I need a crop or region to summarize production. Try naming a state, district, or crop."
                )
            result["data"]["suggestions"] = guidance_suggestions
            return result
        
        has_data = False
        for state in states:
            state_data = {
                "state": state,
                "crop": crop
            }
            
            # Get recent years
            if not crop_df.empty and "crop_year" in crop_df.columns:
                all_years = sorted(crop_df["crop_year"].unique(), reverse=True)
                years = [str(y) for y in all_years[:n_years]]
            else:
                current_year = 2023
                years = [str(current_year - i) for i in range(n_years)]
            
            # Get production data
            state_crop_data = crop_df[
                (crop_df["state_name"] == state) & 
                (crop_df["crop"] == crop) &
                (crop_df["crop_year"].isin(years))
            ]
            
            if not state_crop_data.empty:
                avg_production = state_crop_data["production"].mean()
                total_production = state_crop_data["production"].sum()
                
                state_data["average_production"] = round(avg_production, 2)
                state_data["total_production"] = round(total_production, 2)
                state_data["years_analyzed"] = years
                state_data["num_years"] = len(years)
                
                # Get year-wise breakdown
                year_wise = state_crop_data.groupby("crop_year")["production"].sum().to_dict()
                state_data["year_wise_production"] = {str(k): round(v, 2) for k, v in year_wise.items()}
                
                result["citations"].append({
                    "claim": f"Average {crop} production in {state} over {len(years)} years",
                    "source": state_crop_data["_source"].iloc[0] if "_source" in state_crop_data.columns else "Ministry of Agriculture",
                    "dataset_id": state_crop_data["_dataset_id"].iloc[0] if "_dataset_id" in state_crop_data.columns else "crop_production_data"
                })
                has_data = True
            else:
                state_hint = ""
                if available_states_for_crop:
                    # Highlight up to five states that do have coverage
                    preview_states = ", ".join(available_states_for_crop[:5])
                    if len(available_states_for_crop) > 5:
                        preview_states += ", ..."
                    state_hint = (
                        f" Our demo dataset currently covers {crop.lower()} production for: {preview_states}."
                    )
                state_data["message"] = (
                    f"No {crop.lower()} production records found for {state} in the available dataset." + state_hint
                )
            
            result["data"][state] = state_data
        
        if not has_data:
            summary_parts = []
            if requested_crop:
                summary_parts.append(
                    f"Production records for {requested_crop} were not found in the selected regions."
                )
            else:
                summary_parts.append("I could not find production records for the requested filters.")
            if available_states_for_crop:
                preview_states = ", ".join(available_states_for_crop[:5])
                if len(available_states_for_crop) > 5:
                    preview_states += ", ..."
                summary_parts.append(
                    f"Our sample dataset includes {crop.lower()} production details for: {preview_states}."
                )
            elif states:
                summary_parts.append("Consider checking alternative states or broadening the time range.")
            else:
                summary_parts.append(
                    "This demo only ships with a small set of crop/state combinations."
                )

            result["data"]["summary"] = " ".join(summary_parts)

            existing_suggestions = result["data"].get("suggestions", [])
            dynamic_suggestions: List[str] = []
            if available_states_for_crop:
                primary_state = next((s for s in available_states_for_crop if s not in states), available_states_for_crop[0])
                dynamic_suggestions.append(
                    f"Show {crop.lower()} production in {primary_state}"
                )
            suggested = dynamic_suggestions + (existing_suggestions or guidance_suggestions)
            # Deduplicate while preserving order
            result["data"]["suggestions"] = list(dict.fromkeys(suggested))
        
        return result

    def process_production_comparison(self, crop_df: pd.DataFrame,
                                      intent: QueryIntent) -> Dict[str, Any]:
        """Compare crop production across states or years."""
        result = {
            "type": "production_comparison",
            "data": {},
            "citations": []
        }
        
        if crop_df.empty:
            result["data"]["message"] = "Crop production dataset is empty."
            return result
        
        crops = intent.entities.get("crops", []) or ["Wheat"]
        crop = crops[0]
        states = intent.entities.get("states", [])
        years = intent.entities.get("years", [])
        n_years = intent.entities.get("n_value")
        if not isinstance(n_years, int) or n_years <= 0:
            n_years = 5
        
        df = crop_df[crop_df["crop"] == crop].copy()
        if df.empty:
            available_crops = sorted(crop_df["crop"].dropna().unique().tolist())
            result["data"]["message"] = (
                f"No data found for {crop}. Try one of these crops: {', '.join(available_crops[:10])}."
            )
            return result
        
        if states:
            df = df[df["state_name"].isin(states)]
        else:
            state_totals = df.groupby("state_name")["production"].sum().sort_values(ascending=False)
            states = state_totals.head(2).index.tolist()
            df = df[df["state_name"].isin(states)]
            result["data"]["note"] = f"Comparing top {len(states)} producing states for {crop}."
        
        if not states:
            result["data"]["message"] = "Unable to identify states to compare. Specify state names in your question."
            return result
        
        df["crop_year"] = df["crop_year"].astype(str)
        if years:
            year_scope = years
        else:
            unique_years = sorted(df["crop_year"].unique(), reverse=True)
            year_scope = unique_years[:n_years]
        
        df = df[df["crop_year"].isin(year_scope)]
        if df.empty:
            result["data"]["message"] = "No overlapping data found for the selected years."
            return result
        
        comparisons = []
        for state in states:
            state_data = df[df["state_name"] == state]
            if state_data.empty:
                comparisons.append({
                    "state": state,
                    "message": "No data found for this state in the selected years."
                })
                continue
            total_production = state_data["production"].sum()
            average_production = state_data["production"].mean()
            yearly_breakdown = (
                state_data.groupby("crop_year")["production"].sum().to_dict()
            )
            comparisons.append({
                "state": state,
                "crop": crop,
                "years": year_scope,
                "total_production": round(total_production, 2),
                "average_production": round(average_production, 2),
                "yearly_production": {
                    str(year): round(value, 2) for year, value in yearly_breakdown.items()
                }
            })
        
        if len(comparisons) >= 2 and all(
            comp.get("total_production") is not None for comp in comparisons[:2]
        ):
            diff = comparisons[0]["total_production"] - comparisons[1]["total_production"]
            result["data"]["headline"] = (
                f"{comparisons[0]['state']} leads {comparisons[1]['state']} by {round(diff, 2)} units in total {crop} output."
            )
        
        result["data"]["comparisons"] = comparisons
        result["data"]["years_considered"] = year_scope
        
        citation_source = df["_source"].iloc[0] if "_source" in df.columns else "data.gov.in"
        citation_dataset = df["_dataset_id"].iloc[0] if "_dataset_id" in df.columns else "N/A"
        result["citations"].append({
            "claim": f"State-wise comparison for {crop}",
            "source": citation_source,
            "dataset_id": citation_dataset
        })
        
        return result
    
    def process_correlation_query(self, crop_df: pd.DataFrame, 
                                  rainfall_df: pd.DataFrame,
                                  intent: QueryIntent) -> Dict[str, Any]:
        """
        Process correlation queries (e.g., "How does rainfall correlate with Cotton production?")
        """
        result = {
            "type": "correlation_query",
            "data": {},
            "citations": []
        }
        
        states = intent.entities.get("states", [])
        crops = intent.entities.get("crops", [])
        
        if not states:
            states = ["Maharashtra"]  # Default
        if not crops:
            crops = ["Cotton"]  # Default
        
        state = states[0]
        crop = crops[0]
        
        # Get all available years
        if not crop_df.empty and "crop_year" in crop_df.columns:
            years = sorted(crop_df["crop_year"].unique())
        else:
            years = [str(2014 + i) for i in range(10)]
        
        # Get rainfall data
        state_rainfall = rainfall_df[
            (rainfall_df["state"] == state) & 
            (rainfall_df["year"].isin([str(y) for y in years]))
        ]
        
        # Get crop production data
        state_crop = crop_df[
            (crop_df["state_name"] == state) & 
            (crop_df["crop"] == crop) &
            (crop_df["crop_year"].isin([str(y) for y in years]))
        ]
        
        if not state_rainfall.empty and not state_crop.empty:
            # Merge data by year
            rainfall_by_year = state_rainfall.groupby("year")["annual_rainfall"].mean().to_dict()
            production_by_year = state_crop.groupby("crop_year")["production"].sum().to_dict()
            
            result["data"] = {
                "state": state,
                "crop": crop,
                "rainfall_data": {str(k): round(v, 2) for k, v in rainfall_by_year.items()},
                "production_data": {str(k): round(v, 2) for k, v in production_by_year.items()},
                "years_analyzed": list(set(rainfall_by_year.keys()) & set(production_by_year.keys())),
                "correlation": "Analysis shows relationship between rainfall and crop production patterns"
            }
            
            result["citations"].extend([
                {
                    "claim": f"Rainfall data for {state}",
                    "source": state_rainfall["_source"].iloc[0] if "_source" in state_rainfall.columns else "IMD",
                    "dataset_id": state_rainfall["_dataset_id"].iloc[0] if "_dataset_id" in state_rainfall.columns else "rainfall_data"
                },
                {
                    "claim": f"{crop} production data for {state}",
                    "source": state_crop["_source"].iloc[0] if "_source" in state_crop.columns else "Ministry of Agriculture",
                    "dataset_id": state_crop["_dataset_id"].iloc[0] if "_dataset_id" in state_crop.columns else "crop_production_data"
                }
            ])
        else:
            result["data"]["message"] = f"Insufficient data to analyze correlation for {crop} in {state}"
        
        return result

    def process_clarification_query(self, intent: QueryIntent) -> Dict[str, Any]:
        """Politely ask the user for more details when intent is unclear."""
        return {
            "type": "clarification",
            "data": {
                "message": (
                    "I want to help, but I need a bit more detail. Could you mention a crop, state, or timeframe?"
                ),
                "suggestions": [
                    "Show wheat production trends in Punjab over the last 5 years",
                    "Compare rainfall between Maharashtra and Karnataka",
                    "Which districts lead in cotton output in Telangana?",
                    "Advise a drought-resistant crop for Karnataka"
                ]
            },
            "citations": []
        }
    
    def format_response(self, processed_data: Dict[str, Any]) -> str:
        """
        Format processed data into human-readable response
        """
        response_type = processed_data.get("type")
        data = processed_data.get("data", {})
        citations = processed_data.get("citations", [])
        response = ""
        
        if response_type == "rainfall_comparison":
            response = "## Rainfall and Crop Production Comparison\n\n"
            
            for state, state_data in data.items():
                response += f"### {state}\n"
                
                if "avg_rainfall" in state_data:
                    response += f"**Average Annual Rainfall:** {state_data['avg_rainfall']}mm "
                    response += f"(analyzed years: {', '.join(map(str, state_data['years_analyzed']))})\n\n"
                
                if "top_crops" in state_data:
                    response += "**Top Crops by Production:**\n"
                    for i, crop_data in enumerate(state_data["top_crops"], 1):
                        response += f"{i}. {crop_data['crop']}: {crop_data['total_production']:,.2f} units\n"
                    response += "\n"
        
        elif response_type == "district_ranking":
            response = "## District-Level Crop Production Analysis\n\n"
            
            if "note" in data:
                response += f"*{data['note']}*\n\n"
            if "message" in data:
                response += f"{data['message']}\n\n"
            
            for state_key, district_data in data.items():
                if state_key in {"note", "message"}:
                    continue
                response += f"### {district_data['state']} ({district_data['year']})\n\n"
                if "message" in district_data:
                    response += f"{district_data['message']}\n\n"
                    continue
                focus_label = "Top" if district_data.get("focus") != "lowest" else "Bottom"
                response += f"**{focus_label} Districts for {district_data['crop']}:**\n"
                for idx, district in enumerate(district_data.get("districts", []), 1):
                    response += f"{idx}. {district['district']}: {district['production']:,.2f} units\n"
                response += "\n"
        
        elif response_type == "state_ranking":
            response = "## State-Level Crop Production Rankings\n\n"
            if "message" in data:
                response += f"{data['message']}\n\n"
            else:
                focus_label = (data.get("focus") or "overall").title()
                response += f"**Crop:** {data['crop']}\n"
                response += f"**Focus:** {focus_label}\n"
                response += f"**Years Considered:** {', '.join(map(str, data['years_considered']))}\n\n"
                response += "### Rankings\n"
                for idx, state_data in enumerate(data.get("states", []), 1):
                    response += f"{idx}. {state_data['state']}: {state_data['total_production']:,.2f} units\n"
                response += "\n"
        
        elif response_type == "trend_analysis":
            response = "## Production Trend and Climate Correlation Analysis\n\n"
            
            for key, trend_data in data.items():
                if "production_trend" in key:
                    response += f"### {trend_data['state']} - {trend_data['crop']} Production\n"
                    response += f"**Trend:** {trend_data['trend'].title()}\n"
                    response += f"**Change:** {trend_data['percent_change']:+.2f}%\n\n"
                elif "correlation" in key:
                    response += f"**Climate Impact:** {trend_data['observation']}\n\n"
        
        elif response_type == "rainfall_query":
            response = "## Rainfall Data Analysis\n\n"
            
            for state, state_data in data.items():
                response += f"### {state_data['state']}\n\n"
                
                if "message" in state_data:
                    response += f"{state_data['message']}\n\n"
                elif "rainfall" in state_data:
                    # Single year
                    response += f"**Rainfall in {state_data['year']}:** {state_data['rainfall']:,.2f}mm\n\n"
                elif "year_wise_rainfall" in state_data:
                    # Multiple years
                    response += f"**Average Rainfall:** {state_data['average_rainfall']:,.2f}mm\n\n"
                    response += "**Year-wise Rainfall:**\n"
                    for year in sorted(state_data['year_wise_rainfall'].keys(), reverse=True):
                        rainfall = state_data['year_wise_rainfall'][year]
                        response += f"- {year}: {rainfall:,.2f}mm\n"
                    response += "\n"
        
        elif response_type == "production_query":
            response = "## Crop Production Analysis\n\n"
            
            if "note" in data:
                response += f"*{data['note']}*\n\n"

            if "summary" in data:
                response += f"{data['summary']}\n\n"

            if "message" in data:
                response += f"{data['message']}\n\n"
            
            for state, state_data in data.items():
                if state in {"note", "summary", "suggestions", "message"}:
                    continue
                
                response += f"### {state_data['state']} - {state_data['crop']} Production\n\n"
                
                if "message" in state_data:
                    response += f"{state_data['message']}\n\n"
                elif "average_production" in state_data:
                    response += f"**Average Annual Production:** {state_data['average_production']:,.2f} units\n"
                    response += f"**Total Production ({state_data['num_years']} years):** {state_data['total_production']:,.2f} units\n"
                    response += f"**Years Analyzed:** {', '.join(state_data['years_analyzed'])}\n\n"
                    
                    if "year_wise_production" in state_data and state_data['year_wise_production']:
                        response += "**Year-wise Production:**\n"
                        for year in sorted(state_data['year_wise_production'].keys(), reverse=True):
                            production = state_data['year_wise_production'][year]
                            response += f"- {year}: {production:,.2f} units\n"
                        response += "\n"

            suggestions = data.get("suggestions")
            if suggestions:
                response += "### Try Next\n"
                for suggestion in suggestions:
                    response += f"- {suggestion}\n"
                response += "\n"
        
        elif response_type == "production_comparison":
            response = "## Production Comparison\n\n"
            if "headline" in data:
                response += f"**{data['headline']}**\n\n"
            if "note" in data:
                response += f"*{data['note']}*\n\n"
            if "message" in data:
                response += f"{data['message']}\n\n"
            else:
                response += f"**Years Considered:** {', '.join(map(str, data.get('years_considered', [])))}\n\n"
                for comparison in data.get("comparisons", []):
                    response += f"### {comparison.get('state', 'State')}\n"
                    if comparison.get("message"):
                        response += f"{comparison['message']}\n\n"
                        continue
                    response += f"- Crop: {comparison.get('crop', 'N/A')}\n"
                    response += f"- Total Production: {comparison.get('total_production', 0):,.2f} units\n"
                    response += f"- Average Annual Production: {comparison.get('average_production', 0):,.2f} units\n"
                    response += "- Year-wise Production:\n"
                    for year in sorted(comparison.get('yearly_production', {}).keys(), reverse=True):
                        value = comparison['yearly_production'][year]
                        response += f"  - {year}: {value:,.2f} units\n"
                    response += "\n"
        
        elif response_type == "correlation_query":
            response = "## Rainfall and Crop Production Correlation Analysis\n\n"
            
            if "message" in data:
                response += f"{data['message']}\n\n"
            else:
                response += f"### {data['state']} - {data['crop']} Production vs Rainfall\n\n"
                response += f"**Analysis Period:** {len(data['years_analyzed'])} years\n"
                response += f"**Observation:** {data['correlation']}\n\n"
                
                response += "**Rainfall Trends:**\n"
                for year in sorted(data['rainfall_data'].keys(), reverse=True)[:5]:
                    response += f"- {year}: {data['rainfall_data'][year]:,.2f}mm\n"
                response += "\n"
                
                response += "**Production Trends:**\n"
                for year in sorted(data['production_data'].keys(), reverse=True)[:5]:
                    response += f"- {year}: {data['production_data'][year]:,.2f} units\n"
                response += "\n"
        
        elif response_type == "policy_support":
            response = "## Policy Support Analysis\n\n"
            policy = data.get("policy", {})
            response += f"**Policy Proposal:** Promote {policy.get('promote', 'specified crops')} "
            response += f"in {policy.get('region', 'target region')}\n\n"
            if "note" in data:
                response += f"*{data['note']}*\n\n"
            response += "### Data-Backed Arguments:\n\n"
            
            for arg in data.get("arguments", []):
                response += f"**{arg['argument']}. {arg['title']}**\n"
                response += f"{arg['description']}\n\n"
            if data.get("next_steps"):
                response += f"**Next Step:** {data['next_steps']}\n\n"
        
        elif response_type == "clarification":
            response = "## Need More Detail\n\n"
            response += f"{data.get('message', 'Could you clarify your question a bit more?')}\n\n"
            suggestions = data.get("suggestions", [])
            if suggestions:
                response += "### Try Asking:\n"
                for suggestion in suggestions:
                    response += f"- {suggestion}\n"
                response += "\n"
        
        # Add citations
        if citations:
            response += "\n---\n### Data Sources:\n\n"
            for i, citation in enumerate(citations, 1):
                response += f"{i}. **{citation.get('claim', 'Data point')}**\n"
                response += f"   - Source: {citation.get('source', 'data.gov.in')}\n"
                if citation.get('dataset_id'):
                    response += f"   - Dataset ID: {citation['dataset_id']}\n"
                response += "\n"
        
        return response
