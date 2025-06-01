from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from api.models.requests import ChatRequest
from api.models.responses import Chatresponse
from api.services.agent_service import AgentService
import json
import logging

router = APIRouter(prefix="/chat", tags=["chat"])
agent_services = AgentService()

@router.post("/message", response_model=Chatresponse)
async def send_message(request: ChatRequest):
    """
    Envia uma mensagem para o agente médico.

    Args:
        request (ChatRequest): Dados da requisição contendo a mensagem e o ID da sessão.

    Returns:
        Chatresponse: Resposta do agente médico.
    """
    try:
        logging.info(f"Recebendo mensagem para a sessão {request.session_id}")
        result = await agent_services.process_message(
            message=request.message,
            session_id=request.session_id
        )
        logging.info(f"Mensagem processada com sucesso para a sessão {request.session_id}")
        return Chatresponse(**result)
    except Exception as e:
        logging.error(f"Erro ao processar mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")
    
@router.post("/stream")
async def stream_message(request: ChatRequest):
    """Stream da resposta do agente"""
    async def generate():
        try:
            async for chunk in  agent_services.stream_message(
                message=request.message,
                session_id=request.session_id
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        except Exception as e:
            yield f"data: (json.dumps({'error': str(e)}))\n\n"
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )

@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Recupera o histórico de uma sessão"""
    session = agent_services.sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    return {"messages": session["messages"]}
