import pandas as pd
from typing import Any, Dict
from app.models.schemas import IntentSchema
from app.data.loader import load_csv_to_dataframe
from app.utils.logging_config import logger

class QueryService:
    def __init__(self):
        # In a real heavy app, we might use SQLite for this to save memory,
        # but for small/medium files, Pandas is excellent for complex aggregations.
        self.df = load_csv_to_dataframe()

    def execute_intent(self, intent: IntentSchema) -> Dict[str, Any]:
        if self.df is None or self.df.empty:
            raise ValueError("Data not available")

        # Copy to avoid mutating original
        df = self.df.copy()
        
        # Apply filters
        if intent.filters:
            for col, val in intent.filters.items():
                if col not in df.columns:
                    continue
                if isinstance(val, list):
                    df = df[df[col].isin(val)]
                else:
                    df = df[df[col] == val]

        result: Dict[str, Any] = {}
        
        try:
            # Handle intents
            if intent.intent == "count":
                result["count"] = len(df)
            elif intent.intent == "average":
                if intent.metric and intent.metric in df.columns:
                    result["average"] = df[intent.metric].mean()
            elif intent.intent == "sum":
                if intent.metric and intent.metric in df.columns:
                    result["sum"] = df[intent.metric].sum()
            elif intent.intent == "maximum":
                if intent.metric and intent.metric in df.columns:
                    result["maximum"] = df[intent.metric].max()
            elif intent.intent == "minimum":
                if intent.metric and intent.metric in df.columns:
                    result["minimum"] = df[intent.metric].min()
            elif intent.intent == "group_by":
                if intent.group_by and intent.group_by in df.columns:
                    if intent.aggregation == "average" and intent.metric:
                        grouped = df.groupby(intent.group_by)[intent.metric].mean().reset_index()
                    elif intent.aggregation == "count":
                        grouped = df.groupby(intent.group_by).size().reset_index(name='count')
                    else:
                        grouped = df.groupby(intent.group_by).size().reset_index(name='count')
                    result["rows"] = grouped.to_dict('records')
            elif intent.intent == "list" or intent.intent == "filter":
                if intent.limit:
                    result["rows"] = df.head(intent.limit).to_dict('records')
                else:
                    result["rows"] = df.head(100).to_dict('records') # cap at 100 to avoid huge payloads
            elif intent.intent == "percentage":
                # Assuming filters represent the numerator, and total is denominator
                # Wait, if filters were applied, df is already the numerator. We need original size.
                total_count = len(self.df)
                if total_count > 0:
                    result["percentage"] = round((len(df) / total_count) * 100, 2)
                else:
                    result["percentage"] = 0.0
            elif intent.intent == "top_n":
                if intent.group_by and intent.metric:
                    grouped = df.groupby(intent.group_by)[intent.metric].mean().reset_index()
                    grouped = grouped.sort_values(by=intent.metric, ascending=False).head(intent.limit or 5)
                    result["rows"] = grouped.to_dict('records')
            else:
                result["error"] = f"Unsupported intent: {intent.intent}"
                
            # Clean up numpy types for JSON serialization
            import math
            import numpy as np
            def sanitize(val):
                if isinstance(val, (np.int64, np.int32)): return int(val)
                if isinstance(val, (np.float64, np.float32)): return float(val) if not math.isnan(val) else None
                return val
                
            for k, v in result.items():
                if isinstance(v, list):
                    for row in v:
                        for row_k, row_v in row.items():
                            row[row_k] = sanitize(row_v)
                else:
                    result[k] = sanitize(v)

            return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise ValueError(f"Failed to execute query: {str(e)}")
