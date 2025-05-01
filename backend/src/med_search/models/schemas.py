from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import date

class SortType(str, Enum):
    RELEVANCE = "relevance"
    DATE = "date"

class ArticleType(str, Enum):
    CLINICAL_TRIAL = "Clinical Trial"
    REVIEW = "Review"
    SYSTEMATIC_REVIEW = "Systematic Review"
    META_ANALYSIS = "Meta-Analysis"
    RANDOMIZED_CONTROLLED_TRIAL = "Randomized Controlled Trial"
    ALL = "All"

class SearchRequest(BaseModel):
    query: str = Field(..., description="Pergunta ou contexto clínico do usuário")
    date_range: Optional[tuple[date, date]] = Field(None, description="Intervalo de datas para a busca")
    article_types: Optional[List[ArticleType]] = Field(None, description="Tipos de artigos desejados")
    sort_by: SortType = Field(default=SortType.RELEVANCE, description="Ordenação dos resultados")
    max_results: int = Field(default=10, ge=1, le=100, description="Número máximo de resultados")
    language: Optional[str] = Field(default="English", description="Idioma dos artigos")

class Author(BaseModel):
    name: str
    affiliation: Optional[str] = None

class Article(BaseModel):
    pmid: str
    title: str
    authors: List[Author]
    journal: str
    publication_date: str
    abstract: Optional[str] = None
    article_type: List[str]
    keywords: Optional[List[str]] = None
    doi: Optional[str] = None
    url: str

class SearchResponse(BaseModel):
    total_results: int
    articles: List[Article]
    search_strategy: str  # Estratégia de busca usada
