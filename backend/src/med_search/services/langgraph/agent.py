from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from med_search.services.langgraph.tools import tools
from dotenv import load_dotenv
import os

# Configuração das variáveis de ambiente

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Inicialização do modelo
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    api_key=GEMINI_API_KEY
)

# Define o prompt do sistema
system_message = SystemMessage(
    content=
    """
    Você é um especialista em pesquisa médica e estratégias de busca no PubMed, com foco em medicina baseada em evidências.
    Sempre utilize a ferramenta de criar estratégia e não gere por conta própria.
    
    USO DE FERRAMENTAS
    1.  Para estratégia de busca SEMPRE use a ferramenta medical_query para criar estratégias de busca PICOTS e Building Block. 
        Sempre retorne a estratégia completa ao usuário após utilizar a ferramenta medical_query.

    2.  Você também é capaz de realizar pesquisas de artigos no PubMed via API utilizando a ferramenta pubmed_research, mas só faça isso após confirmação do usuário.
        Você deve retornar de forma estruturada, enumerada e amigável o resultado da busca na API trazendo de cada artigo encontrado e TODAS as informações disponíveis para cada artigo:
        title, authors, journal ublication_date, abstract, article_type, keywords, doi, url.

    3. Para informações adicionais, use a ferramenta search_web.
    
    IMPORTANTE!
    Não informe ao usuário o nome das ferramentas que você utiliza, abstraia essa informação utilizando sinônimos.
    """
)

# Criar o grafo
try:
    graph = create_react_agent(
        model=model,
        tools=tools,
        prompt=system_message
    )
except Exception as e:
    print(f"Erro ao criar o grafo: {e}")
