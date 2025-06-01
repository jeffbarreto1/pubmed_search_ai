from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatMessage(BaseModel):
    content: str = Field(..., description="Conteúdo da mensagem")
    role: str = Field(default="user", description="Papel do remetente")

class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensagem do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Query de busca médica")
    filter: Optional[Dict[str, Any]] = Field(None, description="Filtros de busca")
    max_results: Optional[int] = Field(None, description="Número máximo de resultados")
