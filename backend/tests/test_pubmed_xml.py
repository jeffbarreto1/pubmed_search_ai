import os
from dotenv import load_dotenv

from med_search.services.pubmed import PubMedClient
from med_search.models.schemas import SearchRequest

load_dotenv()
api_key = os.getenv("PUBMED_API_KEY")

final_search_strategy="""
                        ((Parkinson Disease[Mesh] OR parkinson OR parkinsonian) AND 
                        ("Aged"[Mesh] OR elderly OR older) AND 
                        (advanced OR late-stage OR "motor fluctuations")) AND 
                        ("Deep Brain Stimulation"[Mesh] OR "Deep Brain Stimulation") AND 
                        ((pharmacotherapy OR medication OR drug OR drugs OR levodopa OR carbidopa)) AND 
                        ((Dyskinesias[Mesh] OR dyskinesia OR dyskinesias OR "Quality of Life"[Mesh] OR "Quality of Life" OR QOL)) AND 
                        (("Randomized Controlled Trial"[Publication Type] OR "Systematic Review"[Publication Type] OR "Meta-Analysis"[Publication Type]))
                    """

def main ():
    # Chave de API do PubMed, se houver
    client = PubMedClient(api_key=None)

    # Cria a requisição de busca
    request = SearchRequest(
        query=final_search_strategy,
        max_results=5,
        sort_by="relevance"
    )

    # Busqua os artigos
    pmids = client.search_pmids_articles(request)


    articles = client._fetch_articles_details_xml(pmids)
    for article in articles:
        print(f"Título: {article.get('title', [])}")
        print(f"Autores: {', '.join(article.get('authors', []))}")
        structured_abstract = article.get('abstract', {})
        if structured_abstract:
            print("Abstract:")
            for section, text in structured_abstract.items():
                print(f"{section}: {text}")
        else:
            print(f"Abstract: {''.join(article.get('simple_abstract', []))}")
        print(f"keywords: {', '.join(article.get('keywords', []))}")
        print(f"Journal: {article.get('journal',[])}")
        print(f"Tipos de publicação: {', '.join(article.get('article_type', []))}")
        print(f"DOI: {article.get('doi', [])}")
        print(f"Link: {article.get('url',[])}")
        print(f"Data da publicação: {article.get("publication_date",[])}")
        print("---")
    
if __name__ == "__main__":
    main()