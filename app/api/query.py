from fastapi import APIRouter, HTTPException
import time
from app.models.schemas import QueryRequest, QueryResult
from app.services.llm_service import LLMService
from app.services.query_service import QueryService
from app.utils.logging_config import logger

router = APIRouter()
llm_service = LLMService()
query_service = QueryService()

@router.post("/query", response_model=QueryResult)
def process_query(request: QueryRequest):
    start_time = time.time()
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    try:
        logger.info(f"Processing query: {request.question}")
        
        # 1. Extract intent
        intent_obj = llm_service.extract_intent(request.question)
        logger.info(f"Extracted intent: {intent_obj.model_dump()}")
        
        # 2. Execute query
        result_data = query_service.execute_intent(intent_obj)
        
        # 3. Format response
        nl_answer = llm_service.format_response(request.question, result_data, intent_obj.intent)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return QueryResult(
            question=request.question,
            answer=nl_answer,
            intent=intent_obj.intent,
            result=result_data,
            execution_time_ms=execution_time
        )
    except ValueError as ve:
        logger.error(f"Value Error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Internal Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the query.")
