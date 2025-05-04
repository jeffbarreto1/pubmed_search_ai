import os
from dotenv import load_dotenv

from med_search.services.pubmed import PubMedClient
from med_search.models.schemas import SearchRequest

load_dotenv()
api_key = os.getenv("PUBMED_API_KEY")

final_search_strategy="""((Parkinson Disease[Mesh] OR parkinson OR parkinsonian) AND ("Aged"[Mesh] OR elderly OR older) AND (advanced OR late-stage OR "motor fluctuations")) AND ("Deep Brain Stimulation"[Mesh] OR "Deep Brain Stimulation") AND ((pharmacotherapy OR medication OR drug OR drugs OR levodopa OR carbidopa)) AND ((Dyskinesias[Mesh] OR dyskinesia OR dyskinesias OR "Quality of Life"[Mesh] OR "Quality of Life" OR QOL)) AND (("Randomized Controlled Trial"[Publication Type] OR "Systematic Review"[Publication Type] OR "Meta-Analysis"[Publication Type]))"""


def main():
    # Chave de API do PubMed, se houver
    client = PubMedClient(api_key=None)

    # Cria a requisição de busca
    request = SearchRequest(
        query=final_search_strategy,
        max_results=5,
        sort_by="relevance"
    )

    # Busqua os artigos
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

if __name__ == "__main__":
    main()
