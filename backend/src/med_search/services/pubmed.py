import requests
from typing import List, Dict, Optional
from datetime import date
from ..models.schemas import Article, Author, SearchRequest

class PubMedClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def _build_base_params(self) -> Dict:
        """Constrói parâmetros base para as requisições"""
        params = {
            "db": "pubmed",
            "retmode": "json",
        }
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    def search_articles(self, search_request: SearchRequest) -> List[Article]:
        """Realiza a busca de artigos no PubMed"""
        # Primeiro, busca os PMIDs
        search_params = self._build_base_params()
        search_params.update({
            "term": search_request.query,
            "retmax": search_request.max_results,
            "sort": search_request.sort_by
        })

        # Adiciona filtros de data se especificados
        if search_request.date_range:
            start_date, end_date = search_request.date_range
            search_params.update({
                "mindate": start_date.strftime("%Y/%m/%d"),
                "maxdate": end_date.strftime("%Y/%m/%d"),
                "datetype": "pdat"
            })

        # Primeira chamada para obter os PMIDs
        response = requests.get(
            f"{self.BASE_URL}/esearch.fcgi",
            params=search_params
        )
        response.raise_for_status()
        search_results = response.json()

        pmids = search_results["esearchresult"]["idlist"]

        # Se não encontrou resultados, retorna lista vazia
        if not pmids:
            return []

        # Busca os detalhes dos artigos encontrados
        return self._fetch_articles_details(pmids)

    def _fetch_articles_details(self, pmids: List[str]) -> List[Article]:
        """Busca os detalhes dos artigos usando os PMIDs"""
        summary_params = self._build_base_params()
        summary_params["id"] = ",".join(pmids)

        response = requests.get(
            f"{self.BASE_URL}/esummary.fcgi",
            params=summary_params
        )
        response.raise_for_status()

        articles_data = response.json()["result"]
        articles = []

        for pmid in pmids:
            article_data = articles_data[pmid]

            # Converte os dados para modelo utilizado
            article = Article(
                pmid=pmid,
                title=article_data["title"],
                authors=[
                    Author(
                        name=author["name"],
                        affiliation=None
                    )
                    for author in article_data.get("authors", [])
                ],
                journal=article_data["fulljournalname"],
                publication_date=article_data["pubdate"],
                abstract=None,
                article_type=article_data.get("pubtype", []),
                doi=next(
                    (id_obj["value"] for id_obj in article_data["articleids"]
                     if id_obj["idtype"] == "doi"), None
                ),
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            )
            articles.append(article)

        return articles
    