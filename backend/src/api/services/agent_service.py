import logging
import uuid
from datetime import datetime
from typing import Dict, Any, AsyncGenerator
from fastapi import HTTPException
from med_search.agent.langgraph.agent import graph
from api.core.config import get_settings

class AgentService:
    def __init__(self):
        self.settings = get_settings()
        self.sessions: Dict[str, Any] = {}
        self.agent = graph
    
    async def create_session(self) -> str:
        """Cria uma nova sessão do chat"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "messages": [],
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
        return session_id
    async def process_message(
        self,
        message: str,
        session_id: str = None
    ) -> Dict[str, Any]:
        """Processa uma mensagem através do agente LangGraph"""
        if not session_id:
            session_id = await self.create_session()

        # Recupera o histórico da sessão
        session = self.sessions.get(session_id, {})
        messages = session.get("messages", [])

        # Adiciona a mensagem do usuário
        messages.append({"role": "user", "content": message})

        # Processa através do agente LangGraph
        try:
            response = await self.agent.ainvoke({
                "messages": messages,
                "session_id": session_id
            })

            logging.info(f"Response completo do agente: {response}") # Log do response completo

            # Extrai a última mensagem do agente
            agent_message_obj = response["messages"][-1]
            agent_message = agent_message_obj.content
            logging.info(f"Dado da última mensagem: {agent_message_obj}") # Log da última mensagem retornada

            # Extrai os metadados da última mensagem do agente
            response_metadata = getattr(agent_message_obj, "response_metadata", {})
            usage_metadata = getattr(agent_message_obj, "usage_metadata", {})
            type = getattr(agent_message_obj, "type")
        
            # Atualiza a sessão
            messages.append({"role": "assistant", "content": agent_message})
            self.sessions[session_id] = {
                "messages": messages,
                "last_activity": datetime.now()
            }

            # Retorna os dados processados
            return {
                "message": agent_message,
                "session_id": session_id,
                "sources": [],
                "response_metadata": response_metadata,
                "usage_metadata": usage_metadata,
                "type": type,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logging.error(f"Erro ao processar mensagem: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro no agente: {str(e)}")
    async def stream_message(
            self,
            message: str,
            session_id: str = None
    )-> AsyncGenerator[str, None]:
        """Stream da resposta do agente"""
        if not session_id:
            session_id = await self.create_session()
        
        session = self.sessions.get(session_id, {})
        messages = session.get("messages", [])
        messages.append({"role": "user", "content": message})

        async for chunk in self.agent.astream({
            "messages": messages,
            "session_id": session_id
        }):
            if "messages" in chunk:
                yield chunk["messages"][-1].content
