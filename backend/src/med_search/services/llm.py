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
        Você é um especialista em pesquisa médica e estratégias de busca no PubMed.
        Analise a seguinte pergunta clínica e forneça uma estratégia de busca otimizada:

        Pergunta: "{user_query}"

        Retorne APENAS o objeto JSON puro, sem formatação markdown ou marcadores de código. O JSON deve ter a seguinte estrutura:
        {{
            "clinical_concepts": ["lista de conceitos clínicos principais identificados na pergunta"],
            "mesh_terms": ["lista de termos MeSH apropriados, com suas tags"],
            "search_strategy": "estratégia de busca PubMed completa usando os termos MeSH e operadores booleanos"],
            "english_translation": "tradução da pergunta para inglês (se a pergunta original não for em inglês)",
            "start_year": ano inicial do período de busca (se houver),
            "end_year": ano final do período de busca (se houver)
        }}

        - Se a pergunta mencionar um ano específico, defina start_year e end_year com o mesmo valor.
        - Se a pergunta mencionar um intervalo de anos (ex: 2010-2020), defina start_year com o ano inicial e end_year com o ano final.
        - Se a pergunta não mencionar nenhum período de tempo, omita os campos start_year e end_year.

        Exemplo de formato esperado para termos MeSH:
        "mesh_terms": ["Atrial Fibrillation[Mesh]", "Aged[Mesh]", "Renal Insufficiency[Mesh]", "Therapeutics[Mesh]"]

        Exemplo de estratégia de busca:
        "search_strategy": "(Atrial Fibrillation[Mesh]) AND (Aged[Mesh]) AND (Renal Insufficiency[Mesh]) AND (Therapeutics[Mesh])"

        IMPORTANTE: Retorne apenas o JSON, sem marcadores de código ou texto adicional.
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

                # Validar se todas as chaves necessárias estão presentes
                required_keys = ["clinical_concepts", "mesh_terms", "search_strategy"]
                if not all(key in result for key in required_keys):
                    raise ValueError("Resposta incompleta do modelo")
                
                # Extrair start_year e end_year (se presentes)
                start_year = result.get("start_year")
                end_year = result.get("end_year")

                # Validar se os anos são inteiros
                if start_year is not None and not isinstance(start_year, int):
                    raise ValueError("start_year deve ser um inteiro")
                if end_year is not None and not isinstance(end_year, int):
                    raise ValueError("end_year deve ser um inteiro")

                return result

            except json.JSONDecodeError as e:
                print(f"Resposta original do modelo: {response.text}")
                raise ValueError(f"Erro ao processar JSON da resposta: {str(e)}")

        except Exception as e:
            raise Exception(f"Erro ao processar query com Gemini: {str(e)}")

    def improve_search_results(self, initial_results: str) -> str:
        """
        Opcional: Usar o Gemini para melhorar/filtrar os resultados
        """
        pass
    