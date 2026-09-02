import numpy as np

from backend.rag.embeddings import generate_embeddings


texts = [
    "What is a REST API?",
    "Explain REST APIs",
    "What is the weather today?",
]


embeddings = generate_embeddings(texts)


vectors = np.array(embeddings)


def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


similarity_1_2 = cosine_similarity(
    vectors[0],
    vectors[1],
)


similarity_1_3 = cosine_similarity(
    vectors[0],
    vectors[2],
)


print("Similarity between:")
print(f"'{texts[0]}'")
print(f"'{texts[1]}'")
print(":", similarity_1_2)


print()


print("Similarity between:")
print(f"'{texts[0]}'")
print(f"'{texts[2]}'")
print(":", similarity_1_3)
