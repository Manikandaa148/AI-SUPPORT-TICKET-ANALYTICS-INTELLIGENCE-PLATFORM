from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.schemas import AnomalyResult
from app.services.anomaly_service import AnomalyService

router = APIRouter()
anomaly_service = AnomalyService()

@router.get("/anomalies", response_model=List[AnomalyResult])
def get_anomalies(severity: Optional[str] = None):
    try:
        anomalies = anomaly_service.detect_anomalies()
        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
