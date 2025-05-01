from med_search.services.llm import GeminiClient

def main():
    gemini_client = GeminiClient()

    # Solicitar input do usuário
    print("\nDigite sua pergunta clínica:")
    query = input("> ")

    try:
        print("\nProcessando pergunta...")
        result = gemini_client.process_medical_query(query)

        print("\nPergunta original:")
        print(query)

        print("\nConceitos clínicos identificados:")
        for concept in result["clinical_concepts"]:
            print(f"- {concept}")

        print("\nTermos MeSH:")
        for term in result["mesh_terms"]:
            print(f"- {term}")

        print("\nEstratégia de busca PubMed:")
        print(result["search_strategy"])

        # Exibir start_year e end_year (se presentes)
        if "start_year" in result and "end_year" in result:
            print("\nPeríodo de tempo:")
            print(f"  De: {result['start_year']}")
            print(f"  Até: {result['end_year']}")

        if result.get("english_translation"):
            print("\nTradução para inglês:")
            print(result["english_translation"])

    except Exception as e:
        print(f"\nErro: {str(e)}")

if __name__ == "__main__":
    main()
