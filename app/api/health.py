from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.services.llm_service import LLMService
from app.data.database import get_total_tickets

router = APIRouter()
llm_service = LLMService()

@router.get("/health", response_model=HealthResponse)
def health_check():
    tickets_loaded = get_total_tickets()
    llm_status = llm_service.check_health()
    return HealthResponse(
        status="healthy",
        tickets_loaded=tickets_loaded,
        database="connected" if tickets_loaded > 0 else "empty/disconnected",
        llm=llm_status
    )
