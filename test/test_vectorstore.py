import logging

from rag import get_vectorstore


logging.basicConfig(level=logging.INFO)


vectorstore = get_vectorstore()

print("\nVectorstore initialized successfully!")
print(vectorstore)