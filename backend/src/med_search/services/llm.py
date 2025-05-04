import os
import json
import google.generativeai as genai
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def process_medical_query(self, user_query: str) -> Dict:
        """
        Processa a pergunta médica e retorna uma estrutura com termos MeSH e estratégia de busca
        """
        prompt = f"""
        Você é um especialista em pesquisa médica e estratégias de busca no PubMed, com foco em medicina baseada em evidências.

        Analise a seguinte pergunta clínica e desenvolva uma estratégia de busca otimizada usando o método PICOTS e Building Block:

        Pergunta: "{user_query}"

        Siga estas etapas:
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
            "start_year": 2020,
            "end_year": 2025
        }}

        Regras importantes:
        
        1. Use APENAS termos MeSH oficiais da NLM. Não invente ou crie termos MeSH não oficiais.
        2. Para cada componente, inclua tanto termos MeSH quanto palavras-chave relevantes.
        3. Combine termos dentro de cada bloco com OR e use parênteses para agrupar.
        4. Combine os blocos com AND na estratégia final.
        5. Se algum componente do PICOTS não estiver presente na pergunta, defina como null.
        6. Não repita termos MeSH na lista final.
        7. Inclua filtros de data se houver período especificado.
        8. Se a pergunta mencionar tipos específicos de estudo, inclua os filtros apropriados.
        
        EXEMPLO DE BLOCO DE BUSCA:
        "population": "(\"Parkinson Disease\"[Mesh] OR parkinson OR parkinsonian) AND (\"Aged\"[Mesh] OR elderly OR older)"

        IMPORTANTE: Retorne apenas o JSON, sem formatação markdown ou texto adicional.
        """

        try:
            response = self.model.generate_content(prompt)

            # Extrair o JSON da resposta
            try:
                # Limpar a resposta removendo marcadores de código
                response_text = response.text.strip()

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

                return result

            except json.JSONDecodeError as e:
                print(f"Resposta original do modelo: {response.text}")
                raise ValueError(f"Erro ao processar JSON da resposta: {str(e)}")

        except Exception as e:
            raise Exception(f"Erro ao processar query com Gemini: {str(e)}")

    