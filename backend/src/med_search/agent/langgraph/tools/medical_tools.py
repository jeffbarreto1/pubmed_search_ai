from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.2,
    api_key=GEMINI_API_KEY
)

@tool
def medical_query(query: str) -> str:
    """
    Transforma a pergunta clínica em uma estratégia de busca PICOTS
    Args:
        query: Pergunta médica que vai ser utilizada para criar a estratégia
    Returns:
        A estratégia de busca gerada pelo agente ou uma mensagem indicando algum problema ao gerar a estratégia        
    """
    try:
        # Montar o prompt
        prompt = f"""Você é um especialista em pesquisa médica. Analise esta pergunta e crie uma estratégia usando o método PICOTS e Building Block:

        Pergunta: "{query}"
        
        SIGA ESTAS ETAPAS:
            1. Extraia os componentes PICOTS da pergunta:
            - P (População): Quem são os pacientes ou população de interesse?
            - I (Intervenção/Exposição): Qual é a intervenção, tratamento ou exposição principal?
            - C (Comparação): Qual é a intervenção ou exposição de comparação? (se houver)
            - O (Outcomes/Desfechos): Quais são os desfechos ou resultados de interesse?
            - T (Tempo): Qual é o período de tempo relevante? (se especificado)
            - S (Study Design/Desenho do estudo): Quais tipos de estudo são relevantes? (se especificado)

            2. Para cada componente do PICOTS, crie um bloco de busca com:
            - Termos MeSH oficiais da National Library of Medicine (NLM)
            - Palavras-chave relevantes (sinônimos, variações)
            - Combine os termos dentro de cada bloco com OR

            3. Combine todos os blocos relevantes com AND para formar a estratégia final

        REGRAS IMPORTANTES:
            1. Use APENAS termos MeSH oficiais da NLM. Não invente ou crie termos MeSH não oficiais.
            2. Para cada componente, inclua tanto termos MeSH quanto palavras-chave relevantes.
            3. Combine termos dentro de cada bloco com OR e use parênteses para agrupar.
            4. Combine os blocos com AND na estratégia final.
            5. Se algum componente do PICOTS não estiver presente na pergunta, defina como null.
            6. Não repita termos MeSH na lista final.
            7. Inclua filtros de data se houver período especificado.
            8. Se a pergunta mencionar tipos específicos de estudo, inclua os filtros apropriados.

        
        EXEMPLO DE BLOCO DE BUSCA:
            ("Parkinson Disease"[Mesh] OR parkinson OR parkinsonian) AND 
            ("Aged"[Mesh] OR elderly OR older) AND 
            (advanced OR late-stage OR "motor fluctuations") AND 
            ("Deep Brain Stimulation"[Mesh] OR DBS OR "deep brain stimulation therapy") AND
            ("Levodopa"[Mesh] OR levodopa OR carbidopa OR "drug therapy" OR "pharmacological therapy") AND
            ("Dyskinesia, Drug-Induced"[Mesh] OR dyskinesias OR "drug induced dyskinesia") AND 
            ("Quality of Life"[Mesh] OR "quality of life" OR QoL) AND 
            ("Randomized Controlled Trial"[Publication Type] OR "Systematic Review"[Publication Type])
        
        """
        response = model.invoke(prompt)
        return response
    except Exception as e:
        return f"Houve um erro ao gerar a estratégia de busca: {str(e)}"
    