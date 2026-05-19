import logging

from rag import retrieve_documents


logging.basicConfig(level=logging.INFO)


query = "what are General Conduct Policy?"

documents = retrieve_documents(query)

for index, (document, score) in enumerate(documents, start=1):

    print(f"\n--- RESULT {index} ---")

    print(f"Score: {score}")

    print(document.page_content)

    print("\nMetadata:")
    print(document.metadata)