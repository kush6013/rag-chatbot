from backend.rag.retriever import retrieve_context


query = "What is a REST API?"


results = retrieve_context(
    query=query,
    n_results=3,
)


print("Query:")
print(query)

print("\nRetrieved chunks:")


for index, result in enumerate(results, start=1):

    print("\n" + "=" * 60)
    print(f"RESULT {index}")
    print("=" * 60)

    print("Source:", result["source"])
    print("Page:", result["page"])
    print("Distance:", result["distance"])

    print("\nText:")
    print(result["text"])
