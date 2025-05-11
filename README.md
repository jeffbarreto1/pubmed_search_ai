# Med-Search

A modern backend service for intelligent medical literature search, combining Google Gemini LLM and PubMed API.  
This project is designed to help healthcare professionals and researchers find relevant scientific articles more efficiently, using natural language queries and advanced search strategies.

## Features

- **Natural language input:** Users can ask clinical questions in plain language.
- **LLM-powered query analysis:** Google Gemini processes the question, identifies clinical concepts, MeSH terms, and builds an optimized PubMed search strategy.
- **PubMed integration:** Automatically fetches articles from PubMed using the generated search strategy.
- **Date range support:** If the user specifies a publication period, the system filters results accordingly.
- **Clean project structure:** Organized with Poetry, FastAPI, and a clear separation between services, models, and tests.

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/jeffbarreto1/pubmed_search_ai.git
cd med-search/backend
```
### 2. Install dependencies
```bash
poetry install
```
### 3. Configure environment variables

Copy the example

- GOOGLE_API_KEY=your_gemini_api_key_here
- PUBMED_API_KEY=your_pubmed_api_key_here
- TAVILY_API_KEY=your_tavily_api_key_here

### 4. Run a test query

You can run the test script to interact with Gemini and see the PubMed search strategy:
```bash
langgraph dev
```
Or
```bash
langgraph dev --allow-blocking
```
You will be prompted to enter a clinical question. The script will display:
- Identified clinical concepts
- MeSH terms
- PubMed search strategy
- (If present) Date range and English translation

## Technologies Used

- Python 3.13+
- Poetry
- FastAPI (for future API endpoints)
- Google Generative AI (Gemini)
- PubMed E-utilities API
- python-dotenv
- langgraph
- langchain
- tavily-python
