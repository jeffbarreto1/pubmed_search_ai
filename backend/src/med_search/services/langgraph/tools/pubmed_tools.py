from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
import os
import json
from datetime import date

from med_search.services.pubmed import PubMedClient
from med_search.models.schemas import SearchRequest

# Configuração das variáveis de ambiente

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Inicialização do modelo
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    api_key=GEMINI_API_KEY
)

@tool
def pubmed_research(query: str) -> str:
    """
    Utiliza uma estratégia de busca para realizar uma request na API do PubMed. 
    Não utilize IDs ou outros metódos além de uma estratégia de busca.
    Args:
        query: Estratégia de busca
    Returns:
        O resultado da pesquisa retornado pela API da PubMed completo ou uma mensagem indicando que nenhuma informação foi encontrada
    """
    try:
        # Montar o prompt
        prompt = f"""Você é um especialista em buscar artigos na API do PubMed e 
        deve extrair um JSON da estratégia de busca recebida para realizar a request na API. 

        estrategia = {query}

        Retorne APENAS um objeto JSON com a seguinte estrutura, sem formatação markdown ou texto adicional:
            {{
                "picots": {{
                    "population": "descrição da população",
                    "intervention": "descrição da intervenção",
                    "comparison": "descrição da comparação ou null",
                    "outcomes": "descrição dos desfechos",
                    "time": "período de tempo ou null",
                    "study_design": "desenho de estudo ou null"
                }},
                "search_blocks": {{
                    "population": "bloco de busca para população",
                    "intervention": "bloco de busca para intervenção",
                    "comparison": "bloco de busca para comparação ou null",
                    "outcomes": "bloco de busca para desfechos",
                    "time": "bloco de busca para tempo ou null",
                    "study_design": "bloco de busca para desenho de estudo ou null"
                }},
                "final_search_strategy": "estratégia de busca completa",
                "mesh_terms": ["lista de termos MeSH"],
                "start_year": "ano de inicio da busca. caso não forneça, use o ano de 2020",
                "end_year": "ano final da busca. caso não forneça, use o ano de 2025",
            }}
        """
        response = model.invoke(prompt)
        print(response)
        
        # Limpar a resposta removendo marcadores de código
        response_text = str(response.content).strip()

        # Remover marcadores de código markdown se presentes
        if response_text.startswith('```'):
            # Remove a primeira linha (```json)
            response_text = response_text.split('\n', 1)[1]
        if response_text.endswith('```'):
            # Remove a última linha (```)
            response_text = response_text.rsplit('\n', 1)[0]

        # Limpar espaços extras
        response_text = response_text.strip()

        # Converter para dict
        result = json.loads(response_text)

        # Validar chaves necessárias
        required_keys = ["picots", "search_blocks", "final_search_strategy", "mesh_terms"]
        if not all(key in result for key in required_keys):
            raise ValueError("Resposta incompleta do modelo")
        
        # Remover duplicatas das listas
        if "mesh_terms" in result:
            result["mesh_terms"] = list(dict.fromkeys(result["mesh_terms"]))   

        # Cria a requisição de busca
        MAX_RESULTS = 10
        request = SearchRequest(
            query=result["final_search_strategy"],
            max_results=MAX_RESULTS,
            sort_by="relevance"
        )

        # Se houver informação de data no resultado
        if result.get("start_year") and result.get("end_year"):
            request.date_range = (
                date(int(result["start_year"]), 1, 1),
                date(int(result["end_year"]), 12, 31)
            )

        # Busqua os artigos
        client = PubMedClient()
        pubmed_articles = client.search_articles(request)

        return pubmed_articles

    except json.JSONDecodeError as e:
        return f"Erro ao processar a resposta do modelo. Tente novamente. Detalhes: {str(e)}"
