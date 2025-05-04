from med_search.services.llm import GeminiClient
from med_search.services.pubmed import PubMedClient
from med_search.models.schemas import SearchRequest

def main():
    gemini_client = GeminiClient()

    print("\nDigite sua pergunta clínica:")
    query = input("> ")

    try:
        print("\nProcessando pergunta...")
        result = gemini_client.process_medical_query(query)

        print("\nPergunta original:")
        print(query)

        print("\nComponentes PICOTS identificados:")
        for component, value in result["picots"].items():
            if value:  # Só exibe se não for null/None
                print(f"- {component.capitalize()}: {value}")

        print("\nBlocos de busca:")
        for component, block in result["search_blocks"].items():
            if block:  # Só exibe se não for null/None
                print(f"\n{component.upper()}:")
                print(block)

        print("\nEstratégia de busca final:")
        print(result["final_search_strategy"])

        print("\nTermos MeSH utilizados:")
        for term in result["mesh_terms"]:
            print(f"- {term}")

        # Exibir período de tempo (se presente)
        if "start_year" in result and "end_year" in result:
            print("\nPeríodo de tempo:")
            print(f"  De: {result['start_year']}")
            print(f"  Até: {result['end_year']}")

        # Cria a requisição de busca
        request = SearchRequest(
            query=result["final_search_strategy"],
            max_results=5,
            sort_by="relevance"
        )

        # Busqua os artigos
        print("\nBuscando melhores artigos...\n")
        client = PubMedClient(api_key=None)
        articles = client.search_articles(request)

        # Exibe os resultados
        for article in articles:
            print(f"Título: {article.title}")
            print(f"Autores: {', '.join(a.name for a in article.authors)}")
            print(f"Article Type: {', '.join(article.article_type)}")
            print(f"Journal: {article.journal}")
            print(f"DOI: {article.doi}")
            print(f"Link: {article.url}")
            print("---")

    except Exception as e:
        print(f"\nErro: {str(e)}")

if __name__ == "__main__":
    main()
