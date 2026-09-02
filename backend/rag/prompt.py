def build_general_ai_prompt(
    question: str,
    conversation_history: list | None = None,
    language: str = "en",
) -> str:

    conversation_history = conversation_history or []
    language_label = "Hindi" if language == "hi" else "English"

    if conversation_history:
        history_parts = []
        for message in conversation_history:
            history_parts.append(
                f'{message["role"].upper()}: '
                f'{message["content"]}'
            )
        history_text = "\n".join(history_parts)
    else:
        history_text = "No previous conversation."

    return f"""
You are a helpful general AI assistant.

Answer the user's question in {language_label}.
Keep the answer accurate, concise, and helpful.

CONVERSATION HISTORY:
{history_text}

USER QUESTION:
{question}

ANSWER:
"""


def build_rag_prompt(
    question: str,
    context_chunks: list,
    conversation_history: list | None = None,
    language: str = "en",
) -> str:

    conversation_history = conversation_history or []
    language_label = "Hindi" if language == "hi" else "English"

    # --------------------------------
    # Conversation history
    # --------------------------------

    if conversation_history:

        history_parts = []

        for message in conversation_history:
            history_parts.append(
                f'{message["role"].upper()}: '
                f'{message["content"]}'
            )

        history_text = "\n".join(history_parts)

    else:
        history_text = "No previous conversation."

    # --------------------------------
    # No retrieved context
    # --------------------------------

    if not context_chunks:

        return f"""
You are a document question-answering AI assistant.

The user has uploaded documents to a knowledge base.

Answer in {language_label}.

You MUST answer questions ONLY using information
contained in those uploaded documents.

No relevant information was retrieved for the
current question.

CONVERSATION HISTORY:
{history_text}

USER QUESTION:
{question}

RULES:

1. Do not use outside knowledge.
2. Do not guess.
3. Do not invent facts.
4. Do not assume information that is not present
   in the uploaded documents.
5. When a value is not explicitly stated in the
   uploaded document, say that it is not mentioned
   in the uploaded document instead of guessing.
6. If the user asks about internship duration or
   probation period, do not confuse the two.
   If the document mentions probation but not the
   total internship length, say that the total
   internship length is not explicitly stated.
7. If the information cannot be found, respond:

"I couldn't find this information in the
available uploaded documents."

Return only the answer.
"""

    # --------------------------------
    # Build document context
    # --------------------------------

    context_parts = []

    for index, chunk in enumerate(context_chunks, start=1):

        source = chunk.get("source", "Unknown document")
        page = chunk.get("page", "Unknown")
        text = chunk.get("text", "")

        context_parts.append(
            f"""
SOURCE {index}
Document: {source}
Page: {page}

CONTENT:
{text}
"""
        )

    context = "\n".join(context_parts)

    # --------------------------------
    # Detect broad questions
    # --------------------------------

    question_lower = question.lower().strip()

    overview_keywords = [
        "tell me about",
        "about the company",
        "about this company",
        "about this document",
        "give me an overview",
        "overview",
        "summarize",
        "summary",
        "what is this company",
        "what does the company do",
        "what is the company about",
        "describe the company",
        "describe this document",
        "main services",
        "main products",
        "what are the services",
        "what does this document contain",
    ]

    is_overview_question = any(
        keyword in question_lower
        for keyword in overview_keywords
    )

    # --------------------------------
    # Different instructions for
    # overview vs specific questions
    # --------------------------------

    if is_overview_question:

        answer_instruction = """
The user is asking for a broad overview.

Use MULTIPLE relevant sources from the provided
context when appropriate.

Combine related information from the retrieved
documents to create a useful overview.

For example, if the documents contain information
about the company, its services, products,
customers, mission, policies, or other relevant
information, combine the relevant information.

Do NOT invent missing company details.

If only partial information is available, clearly
state that the overview is based on the information
available in the uploaded documents.
"""

    else:

        answer_instruction = """
The user is asking a specific question.

Find the answer in the supplied document context.

Use the most relevant source or sources.

If the answer is not supported by the context,
do not guess or use outside knowledge.
"""

    # --------------------------------
    # Final RAG prompt
    # --------------------------------

    return f"""
You are an AI assistant that answers questions
about documents uploaded by the user.

Your job is to answer the user's question using
ONLY the supplied document context.

CONVERSATION HISTORY:
{history_text}

UPLOADED DOCUMENT CONTEXT:
{context}

CURRENT USER QUESTION:
{question}

{answer_instruction}

IMPORTANT RULES:

1. Use ONLY information from the uploaded
   document context.

2. Do NOT use outside knowledge.

3. Do NOT hallucinate.

4. Do NOT invent names, dates, statistics,
   locations, services, products, employees,
   financial information, or other facts.

5. You may combine information from multiple
   retrieved document chunks when necessary.

6. Conversation history may be used only to
   understand references such as:
   "it", "they", "this", "that", etc.

7. If the answer cannot be supported by the
   uploaded documents, say:

"I couldn't find this information in the
available uploaded documents."

8. For internship duration or probation-related
   questions, be careful not to confuse
   probation period with overall internship length.
   If the document mentions probation but not the
   total duration, explicitly say that the total
   internship duration is not mentioned.

9. Keep the answer clear and natural.

10. For an overview question, provide a concise
    summary using the relevant information found
    in the uploaded documents.

ANSWER:
"""
