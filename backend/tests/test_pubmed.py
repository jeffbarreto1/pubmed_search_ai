import os
from dotenv import load_dotenv

from med_search.services.pubmed import PubMedClient
from med_search.models.schemas import SearchRequest

load_dotenv()
api_key = os.getenv("PUBMED_API_KEY")


def main():
    # Chave de API do PubMed, se houver
    client = PubMedClient(api_key=None)

    # Cria a requisição de busca
    request = SearchRequest(
        query="diabetes treatment",
        max_results=5,
        sort_by="relevance"
    )

    # Busqua os artigos
    articles = client.search_articles(request)

    # Exibe os resultados
    for article in articles:
        print(f"Título: {article.title}")
        print(f"Autores: {', '.join(a.name for a in article.authors)}")
        print(f"Journal: {article.journal}")
        print(f"Link: {article.url}")
        print("---")

if __name__ == "__main__":
    main()
