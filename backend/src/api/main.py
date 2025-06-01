from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat
from api.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Med-Research API",
    description= "API para agente de busca médica",
    version="1.0.0"
)

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["", ""], # URLs do front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Rotas
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Med-Research API está funcionando!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

