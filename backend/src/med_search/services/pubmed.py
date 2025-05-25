import os
import requests
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from datetime import date
from ..models.schemas import Article, Author, SearchRequest
from dotenv import load_dotenv

load_dotenv()

class PubMedClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, api_key: Optional[str] = None):
        api_key = os.getenv("PUBMED_API_KEY")
        self.api_key = api_key

    def _build_base_params(self, format_type: str = "json") -> Dict:
        """Constrói parâmetros base para as requisições"""
        retmode = "xml" if format_type.lower() == "xml" else "json"
        params = {
            "db": "pubmed",
            "retmode": retmode,
        }
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    def search_pmids_articles(self, search_request: SearchRequest) -> List[Article]:
        """Realiza busca no PubMed por meio de uma estratégia de busca para obter IDs de artigos"""
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
        return pmids

    def search_articles(self, search_request: SearchRequest) -> List[Article]:
        """Realiza a busca de artigos no PubMed"""
        # Primeiro, busca os PMIDs
        pmids = self.search_pmids_articles(search_request)

        # Se não encontrou resultados, retorna lista vazia
        if not pmids:
            return []

        # Busca os detalhes dos artigos encontrados
        return self._fetch_articles_details_xml(pmids)

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
    
    def _fetch_articles_details_xml(self, pmids: List) -> List[Article]:

        params = self._build_base_params("xml")
        params["id"] = ",".join(pmids)
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/efetch.fcgi", 
                params=params
            )
            response.raise_for_status()

            # Parsear o XML
            root = ET.fromstring(response.content)

            # Inicializar o dicionário de resultado
            articles = []

            # Encontrar todos os elementos PubmedArticle
            pubmed_articles = root.findall(".//PubmedArticle")

            # Iterar sobre cada artigo
            for article_element in pubmed_articles:
                # Inicializar o dicionário para este artigo
                article_data = {}

                # Extrair PMID
                pmid_element = article_element.find(".//PMID")
                if pmid_element is not None and pmid_element.text:
                    article_data["pmid"] = pmid_element.text

                # Extrair o título
                title_element = article_element.find(".//ArticleTitle")
                if title_element is not None and title_element.text:
                    article_data["title"] = title_element.text

                # Extrair o abstract
                abstract_texts = article_element.findall(".//AbstractText")
                if abstract_texts:
                    # Versão simples (texto completo)
                    full_abstract = " ".join([text.text for text in abstract_texts if text.text])
                    article_data["simple_abstract"] = full_abstract

                    # Versão estruturada (por categoria)
                    structured_abstract = {}
                    for text in abstract_texts:
                        if text.text:
                            # Obter a categoria do abstract
                            category = text.get("NlmCategory", "")
                            label = text.get("Label", "")

                            # Usar Label se disponível, senão usar NlmCategory
                            section_title = label if label else category

                            if section_title:
                                structured_abstract[section_title] = text.text

                    # Adicionar o abstract estruturado se houver seções
                    if structured_abstract:
                        article_data["abstract"] = structured_abstract

                # Extrair autores
                authors = []
                author_elements = article_element.findall(".//Author")
                for author in author_elements:
                    last_name = author.find("LastName")
                    fore_name = author.find("ForeName")
                    if last_name is not None and last_name.text:
                        author_name = last_name.text
                        if fore_name is not None and fore_name.text:
                            author_name = f"{fore_name.text} {author_name}"
                        authors.append(author_name)

                if authors:
                    article_data["authors"] = authors

                # Extrair DOI
                doi_element = article_element.find(".//ArticleId[@IdType='doi']")
                if doi_element is not None and doi_element.text:
                    article_data["doi"] = doi_element.text

                # Extrair data de publicação
                pub_date = article_element.find(".//PubDate")
                if pub_date is not None:
                    year = pub_date.find("Year")
                    month = pub_date.find("Month")
                    day = pub_date.find("Day")

                    date_parts = []
                    if year is not None and year.text:
                        date_parts.append(year.text)
                    if month is not None and month.text:
                        date_parts.append(month.text)
                    if day is not None and day.text:
                        date_parts.append(day.text)

                    if date_parts:
                        article_data["publication_date"] = "/".join(date_parts)

                # Extrair nome do journal
                journal_title = article_element.find(".//Journal/Title")
                if journal_title is not None and journal_title.text:
                    article_data["journal"] = journal_title.text

                # Extrair keywords
                keyword_elements = article_element.findall(".//Keyword")
                if keyword_elements:
                    article_data["keywords"] = [kw.text for kw in keyword_elements if kw.text]

                # Extrair tipos de publicação
                article_type = []
                publication_type_elements = article_element.findall(".//PublicationType")
                if publication_type_elements:
                    article_type = [pt.text for pt in publication_type_elements if pt.text]
                article_data["article_type"] = article_type

                # Adicionar URL do artigo
                if "pmid" in article_data:
                    article_data["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{article_data['pmid']}/"

                # Adicionar o artigo à lista
                articles.append(article_data)

            return articles

        except Exception as e:
            print(f"Erro ao buscar detalhes do artigo {pmids}: {str(e)}")
            return None
