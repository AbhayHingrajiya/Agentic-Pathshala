import logging

from rag import get_embeddings

logging.basicConfig(level=logging.INFO)

embeddings = get_embeddings()

sentence = "This is a test sentence."
query_vector = embeddings.embed_query(sentence)

print(f"\nVector length: {len(query_vector)}")

print("\nFirst 10 values:")
print(query_vector[:10])