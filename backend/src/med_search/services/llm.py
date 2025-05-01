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

        Retorne APENAS um objeto JSON com a seguinte estrutura, sem repetições ou texto adicional:
        {{
            "clinical_concepts": ["lista única de conceitos clínicos principais"],
            "mesh_terms": ["lista única de termos MeSH, sem duplicatas"],
            "search_strategy": "estratégia de busca PubMed usando operadores booleanos (AND, OR) e parênteses para agrupamento",
            "english_translation": "tradução para inglês (se a pergunta não for em inglês)",
            "start_year": ano inicial (se mencionado na pergunta),
            "end_year": ano final (se mencionado na pergunta)
        }}

        Regras importantes:
        1. Retorne apenas termos MeSH oficiais, conforme definidos pela NLM. Não crie ou invente termos MeSH que não existam na base oficial
        2. Não repita conceitos ou termos MeSH
        3. Agrupe termos relacionados com OR e diferentes conceitos com AND
        4. Use parênteses para estruturar a busca adequadamente
        5. Inclua filtros de data se houver período especificado
        6. Se mencionados, inclua filtros de tipo de estudo (ex: [article_types])
        7. Se a pergunta mencionar um ano específico, defina start_year e end_year com o mesmo valor
        8. Se a pergunta mencionar um intervalo de anos (ex: 2010-2020), defina start_year com o ano inicial e end_year com o ano final
        9. Se a pergunta não mencionar nenhum período de tempo, omita os campos start_year e end_year

        Exemplo de resposta bem estruturada:
        {{
            "clinical_concepts": ["Parkinson's Disease", "Elderly", "Drug Therapy"],
            "mesh_terms": [
                "Parkinson Disease[Mesh]",
                "Aged[Mesh]",
                "Drug Therapy[Mesh]",
                "Randomized Controlled Trial[Publication Type]"
            ],
            "search_strategy": "((Parkinson Disease[Mesh]) AND (Aged[Mesh]) AND (Drug Therapy[Mesh])) AND (Randomized Controlled Trial[Publication Type])",
            "start_year": 2020,
            "end_year": 2024,
            "english_translation": "Tradução da pergunta para inglês (se a pergunta original não for em inglês). Se a pergunta já vier em inglês retornar vazio."
        }}

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

                # Remover duplicatas das listas
                if "clinical_concepts" in result:
                    result["clinical_concepts"] = list(dict.fromkeys(result["clinical_concepts"]))
                if "mesh_terms" in result:
                    result["mesh_terms"] = list(dict.fromkeys(result["mesh_terms"]))

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
    