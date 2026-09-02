QUESTION_SUITE = [
    {"category": "Direct", "domain": "Company Information", "question": "What is the company name?"},
    {"category": "Direct", "domain": "Products/Services", "question": "What services does the company provide?"},
    {"category": "Direct", "domain": "HR Policies", "question": "What are the company working hours?"},
    {"category": "Direct", "domain": "Leave Policy", "question": "How many leave days are allowed?"},
    {"category": "Direct", "domain": "Internship Policy", "question": "How long is the internship?"},
    {"category": "Direct", "domain": "FAQs", "question": "What documents are required for an internship?"},
    {"category": "Contextual", "domain": "Company Information", "question": "Tell me more about the company."},
    {"category": "Contextual", "domain": "Products/Services", "question": "Does it offer custom software solutions?"},
    {"category": "Contextual", "domain": "Leave Policy", "question": "What about leave for emergencies?"},
    {"category": "Paraphrased", "domain": "Internship Policy", "question": "For how many months does the internship usually last?"},
    {"category": "Paraphrased", "domain": "HR Policies", "question": "When does the workday normally begin and end?"},
    {"category": "Out-of-scope", "domain": "General", "question": "What is the weather today?"},
    {"category": "Out-of-scope", "domain": "General", "question": "What is the CEO salary?"},
    {"category": "Ambiguous", "domain": "Company Information", "question": "Tell me about the company."},
    {"category": "Ambiguous", "domain": "FAQs", "question": "What documents do I need?"},
]


def test_question_suite_contains_15_cases():
    assert len(QUESTION_SUITE) >= 15

    categories = {item["category"] for item in QUESTION_SUITE}
    assert {"Direct", "Contextual", "Paraphrased", "Out-of-scope", "Ambiguous"}.issubset(categories)

    domains = {item["domain"] for item in QUESTION_SUITE}
    assert {"Company Information", "Products/Services", "HR Policies", "Leave Policy", "Internship Policy", "FAQs"}.issubset(domains)

    for item in QUESTION_SUITE:
        assert item["question"].strip()
