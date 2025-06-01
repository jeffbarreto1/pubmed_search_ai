from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Chatresponse(BaseModel):
    message: str = Field(..., description="Resposta do agente")
    session_id: str = Field(..., description="Id da Sessão")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Fontes utilizadas")
    response_metadata: Optional[Dict[str, Any]] = None
    usage_metadata: Optional[Dict[str, Any]] = None
    # tool_calls: Optional[List[Dict[str, Any]]] = None
    type: Optional[str]
    timestamp: datetime = Field(default_factory=datetime.now)

class SearchResult(BaseModel):
    title: str
    abstract: str
    authors: List[str]
    journal: str
    pubmed_id: str
    doi: Optional[str]
    publication_date: Optional[str] 
    relevance_score: Optional[float]

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_found: int
    query_used: str
    execution_time: float

