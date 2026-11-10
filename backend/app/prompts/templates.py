"""
Prompt templates.

Every prompt is grounded: the LLM is instructed to answer ONLY from the
provided context and to explicitly say so when the context is insufficient,
which is the primary lever for reducing hallucination in a RAG system.
"""
from __future__ import annotations

BASE_GROUNDING_RULE = """You are a meticulous research assistant. You must answer using ONLY the
information contained in the CONTEXT below. Do not use outside knowledge, and do not guess.
If the context does not contain enough information to answer, say so explicitly rather than
inventing an answer. When you state a fact, keep it traceable to the context provided.
"""

CHAT_TEMPLATE = BASE_GROUNDING_RULE + """
CONTEXT:
{context}

CONVERSATION HISTORY:
{history}

USER QUESTION:
{question}

Answer clearly and concisely. If you rely on a specific part of the context, refer to it
naturally (e.g. "the methodology section explains..."). If the answer isn't in the context,
say the papers provided don't cover it.
"""

SUMMARY_TEMPLATES: dict[str, str] = {
    "executive": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

Write a 4-6 sentence executive summary of this paper for a busy reader: what problem it
addresses, what it proposes, and what the headline result is.
""",
    "detailed": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

Write a detailed, structured summary (400-600 words) covering: background/motivation,
proposed approach, experimental setup, key results, and conclusions. Use short paragraphs.
""",
    "contributions": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

List the paper's key contributions as a concise bulleted list (3-6 bullets). Each bullet
should be a single, specific, verifiable claim grounded in the context.
""",
    "methodology": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

Explain the methodology used in this paper: the overall approach, model/algorithm design,
and any notable technical choices. Use clear step-by-step structure where applicable.
""",
    "dataset": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

Describe the dataset(s) used: name, size, source, and any preprocessing steps mentioned.
If multiple datasets are used, list each separately.
""",
    "results": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

Summarize the experimental results, including key metrics and how the proposed approach
compares to baselines, exactly as reported in the context.
""",
    "limitations": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

List the limitations of this work as stated or clearly implied in the paper. If the paper
does not explicitly discuss limitations, say so rather than inventing them.
""",
    "future_work": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

List the future work or open directions mentioned in the paper as bullet points.
""",
    "novelty": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

Explain what is novel about this paper relative to prior work, based only on how the
authors position their contribution in the context.
""",
    "practical_applications": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

Based on the paper's findings, describe realistic practical applications or use cases
this work could enable.
""",
    "eli10": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

Explain this paper as if to a curious 10-year-old: simple language, short sentences,
one relatable analogy. Avoid jargon; where a technical term is unavoidable, define it simply.
""",
    "viva": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

Generate 8-10 likely viva/thesis-defense questions an examiner might ask about this paper,
grouped by topic (motivation, methodology, results, limitations). Keep questions specific
to what's actually in the context.
""",
    "interview_questions": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

Generate 6-8 interview-style technical questions that test understanding of this paper's
core ideas, along with a one-line model answer for each, grounded in the context.
""",
    "quiz": BASE_GROUNDING_RULE + """
CONTEXT:
{context}

Create a 5-question multiple-choice quiz testing comprehension of this paper. For each
question provide 4 options (A-D), mark the correct answer, and give a one-sentence
explanation referencing the context.
""",
}

LITERATURE_REVIEW_TEMPLATE = BASE_GROUNDING_RULE + """
CONTEXT (excerpts from multiple papers, each labeled with its source):
{context}

Write a literature review paragraph (200-350 words) that synthesizes these papers: what
they collectively address, how their approaches relate or differ, and what gaps remain.
Refer to papers by title when mentioning specific claims.
"""

RESEARCH_GAP_TEMPLATE = BASE_GROUNDING_RULE + """
CONTEXT (excerpts from multiple papers):
{context}

Based only on the limitations and future work sections of these papers, identify 3-5
research gaps that remain unaddressed. Present as a bulleted list with a one-line
justification for each, referencing which paper(s) support it.
"""

COMPARE_TEMPLATE = BASE_GROUNDING_RULE + """
CONTEXT (excerpts from multiple papers, each labeled with its source paper title):
{context}

Produce a Markdown comparison table with one row per paper and one column per aspect:
{aspects}
If an aspect isn't discussed for a given paper, write "Not specified" instead of guessing.
Output ONLY the markdown table, nothing else.
"""


def format_chat_prompt(context: str, history: str, question: str) -> str:
    return CHAT_TEMPLATE.format(context=context, history=history or "(none)", question=question)


def format_summary_prompt(summary_type: str, context: str) -> str:
    template = SUMMARY_TEMPLATES.get(summary_type, SUMMARY_TEMPLATES["executive"])
    return template.format(context=context)


def format_compare_prompt(context: str, aspects: list[str]) -> str:
    return COMPARE_TEMPLATE.format(context=context, aspects=", ".join(aspects))


def format_literature_review_prompt(context: str) -> str:
    return LITERATURE_REVIEW_TEMPLATE.format(context=context)


def format_research_gap_prompt(context: str) -> str:
    return RESEARCH_GAP_TEMPLATE.format(context=context)
