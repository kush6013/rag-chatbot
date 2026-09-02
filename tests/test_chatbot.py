import requests


API_URL = "http://127.0.0.1:8000/api/chat"


TEST_CASES = [
    {
        "id": 1,
        "category": "Direct",
        "question": "How long is the internship?",
        "expected": "6 months",
    },
    {
        "id": 2,
        "category": "Direct",
        "question": "What are the company working hours?",
        "expected": "10:00 AM to 6:30 PM",
    },
    {
        "id": 3,
        "category": "Direct",
        "question": "Where is the company located?",
        "expected": "Bengaluru",
    },
    {
        "id": 4,
        "category": "Direct",
        "question": "What services does TechNova provide?",
        "expected": "web development",
    },
    {
        "id": 5,
        "category": "Direct",
        "question": "Who can apply for an internship?",
        "expected": "students",
    },
    {
        "id": 6,
        "category": "Direct",
        "question": "What documents are required for an internship?",
        "expected": "resume",
    },
    {
        "id": 7,
        "category": "Direct",
        "question": "Does the company provide an internship certificate?",
        "expected": "certificate",
    },
    {
        "id": 8,
        "category": "Paraphrased",
        "question": "For how many months does the internship normally last?",
        "expected": "6 months",
    },
    {
        "id": 9,
        "category": "Paraphrased",
        "question": "When does the company's normal workday start and finish?",
        "expected": "10:00 AM to 6:30 PM",
    },
    {
        "id": 10,
        "category": "Follow-up",
        "question": "How long is the internship?",
        "expected": "6 months",
        "conversation_id": "memory-test",
    },
    {
        "id": 11,
        "category": "Follow-up",
        "question": "Is it remote?",
        "expected": "hybrid",
        "conversation_id": "memory-test",
    },
    {
        "id": 12,
        "category": "Out-of-scope",
        "question": "What is the CEO salary?",
        "expected": "couldn't find",
    },
    {
        "id": 13,
        "category": "Out-of-scope",
        "question": "What is the weather today?",
        "expected": "couldn't find",
    },
    {
        "id": 14,
        "category": "Ambiguous",
        "question": "Tell me about the company.",
        "expected": "TechNova",
    },
    {
        "id": 15,
        "category": "Ambiguous",
        "question": "What documents do I need?",
        "expected": "documents",
    },
]


def send_question(question, conversation_id="default"):

    response = requests.post(
        API_URL,
        json={
            "message": question,
            "conversation_id": conversation_id,
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def run_tests():

    results = []

    print("\n")
    print("=" * 70)
    print("RAG CHATBOT TEST REPORT")
    print("=" * 70)

    for test in TEST_CASES:

        print(
            f"\nTest {test['id']}: "
            f"{test['category']}"
        )

        print(
            f"Question: {test['question']}"
        )

        conversation_id = test.get(
            "conversation_id",
            f"test-{test['id']}",
        )

        try:

            data = send_question(
                test["question"],
                conversation_id,
            )

            answer = data.get(
                "answer",
                "",
            )

            sources = data.get(
                "sources",
                [],
            )

            passed = (
                test["expected"].lower()
                in answer.lower()
            )

            status = (
                "PASS"
                if passed
                else "FAIL"
            )

            print(
                f"Expected keyword: "
                f"{test['expected']}"
            )

            print(
                f"Actual answer: {answer}"
            )

            print(
                f"Sources: {len(sources)}"
            )

            print(
                f"Result: {status}"
            )

            results.append(
                {
                    "id": test["id"],
                    "category": test["category"],
                    "question": test["question"],
                    "expected": test["expected"],
                    "actual": answer,
                    "sources": len(sources),
                    "status": status,
                }
            )

        except Exception as error:

            print(
                f"Result: ERROR - {error}"
            )

            results.append(
                {
                    "id": test["id"],
                    "category": test["category"],
                    "question": test["question"],
                    "expected": test["expected"],
                    "actual": str(error),
                    "sources": 0,
                    "status": "ERROR",
                }
            )

    # --------------------------------
    # Summary
    # --------------------------------

    passed = sum(
        1
        for result in results
        if result["status"] == "PASS"
    )

    failed = sum(
        1
        for result in results
        if result["status"] == "FAIL"
    )

    errors = sum(
        1
        for result in results
        if result["status"] == "ERROR"
    )

    total = len(results)

    print("\n")
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"Total tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print(f"Errors      : {errors}")

    if total:
        accuracy = (
            passed / total
        ) * 100

        print(
            f"Pass rate   : {accuracy:.2f}%"
        )

    print("=" * 70)


if __name__ == "__main__":
    run_tests()
