from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from dotenv import load_dotenv

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

@tool
def search_query(query: str) -> str:
    """
    Busca informações na web baseada na consulta fornecida.
    Args:
        query: Termos para buscar na web
    Returns:
        As informações encontradas na web ou uma mensagem indicando que nenhuma informação foi encontrada.
        Se a API retornar um erro, abstratia o erro com uma mensagem amigável ao usuário.
    """
    try:
        tavily_search = TavilySearchResults(
            max_results=2,
            api_key=TAVILY_API_KEY
        )
        results = tavily_search.invoke(query)
        return str(results)
    except Exception as e:
        return f"Houve um erro ao buscar dados na web: {str(e)}"
    