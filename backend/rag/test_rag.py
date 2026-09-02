from backend.rag.rag_pipeline import answer_question


question = "What is a REST API?"


result = answer_question(
    question=question,
    n_results=3,
)


print("\n" + "=" * 60)
print("QUESTION")
print("=" * 60)

print(question)


print("\n" + "=" * 60)
print("ANSWER")
print("=" * 60)

print(result["answer"])


print("\n" + "=" * 60)
print("SOURCES")
print("=" * 60)


for source in result["sources"]:

    print(
        f"- {source['source']} "
        f"(Page {source['page']})"
    )
