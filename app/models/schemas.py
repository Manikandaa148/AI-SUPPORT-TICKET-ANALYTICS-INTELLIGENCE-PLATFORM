from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class QueryRequest(BaseModel):
    question: str = Field(..., description="The natural language question to ask")

class QueryResult(BaseModel):
    question: str
    answer: str
    intent: str
    result: Dict[str, Any]
    execution_time_ms: int

class AnomalyResult(BaseModel):
    ticket_id: str
    severity: str
    anomaly_type: str
    reason: str
    detected_value: Optional[float] = None
    threshold: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    tickets_loaded: int
    database: str
    llm: str

class IntentSchema(BaseModel):
    intent: str = Field(..., description="The type of operation (e.g., count, average, sum, filter, list, group_by)")
    metric: Optional[str] = Field(None, description="The column to perform aggregation on (e.g., resolution_time_hrs)")
    aggregation: Optional[str] = Field(None, description="Aggregation function (e.g., average, sum, minimum, maximum)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Dictionary of filters (e.g., {'priority': 'Critical'})")
    group_by: Optional[str] = Field(None, description="Column to group by (e.g., category)")
    limit: Optional[int] = Field(None, description="Maximum number of rows to return")
