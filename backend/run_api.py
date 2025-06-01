import uvicorn
from src.api.core.config import get_settings
import logging

# Configuração básica do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="med_search.log",  # Nome do arquivo de log
    filemode="a"  # Modo de escrita (append)
)

# Teste de logging
logging.info("Configuração de logging inicializada com sucesso.")

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
