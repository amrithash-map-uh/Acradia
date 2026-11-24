import json
import math
import os
import re
from collections import Counter
from typing import List, Optional, Tuple

import httpx

from ..models.db_models import Scheme
from ..models.schemas import AssistantResponse, CitationOut

DISCLAIMER = (
    "This response is grounded in SAHAAY's curated scheme dataset for informational "
    "guidance only and is not an official government eligibility decision."
)

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "for",
    "from", "how", "i", "in", "is", "it", "me", "my", "of", "on", "or",
    "that", "the", "this", "to", "what", "when", "where", "which", "who",
    "with", "am", "eligible", "scheme", "schemes", "about", "tell",
}


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def _scheme_document(scheme: Scheme) -> str:
    rules = json.loads(scheme.eligibility_rules_json)
    conditions = " ".join(rules.get("conditions", []))
    return (
        f"{scheme.name} {scheme.category} {scheme.slug} "
        f"{scheme.description} {scheme.benefits} {conditions} "
        f"{scheme.application_guidance}"
    )


def retrieve_relevant_schemes(
    question: str,
    schemes: List[Scheme],
    scheme_slug: Optional[str] = None,
    top_k: int = 3,
) -> List[Tuple[Scheme, float]]:
    """Rank schemes using lightweight TF-IDF similarity plus optional focus scheme boost."""
    if not schemes:
        return []

    query_tokens = _tokenize(question)
    docs = [_tokenize(_scheme_document(s)) for s in schemes]
    num_docs = len(docs)

    doc_freq: Counter = Counter()
    for tokens in docs:
        doc_freq.update(set(tokens))

    scored: List[Tuple[Scheme, float]] = []
    for scheme, tokens in zip(schemes, docs):
        tf = Counter(tokens)
        score = 0.0
        for q_tok in query_tokens:
            if q_tok in tf:
                idf = math.log((num_docs + 1) / (doc_freq[q_tok] + 1)) + 1.0
                score += tf[q_tok] * idf
        if scheme_slug and scheme.slug == scheme_slug:
            score += 100.0
        scored.append((scheme, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    positive = [item for item in scored if item[1] > 0]
    return positive[:top_k] if positive else scored[:1]


def _format_grounded_fallback(
    question: str,
    ranked: List[Tuple[Scheme, float]],
) -> str:
    if not ranked:
        return "No scheme records are available in the knowledge base right now."

    q_lower = question.lower()
    lines: List[str] = []
    for scheme, _ in ranked[:2]:
        rules = json.loads(scheme.eligibility_rules_json)
        conditions = rules.get("conditions", [])

        parts = [f"**{scheme.name}** ({scheme.category})"]
        if any(word in q_lower for word in ("apply", "register", "document", "how", "portal")):
            parts.append(f"How to apply: {scheme.application_guidance}")
        if any(word in q_lower for word in ("benefit", "money", "amount", "cover", "loan", "pension", "get")):
            parts.append(f"Benefits: {scheme.benefits}")
        if any(word in q_lower for word in ("eligib", "who", "income", "age", "criteria", "qualify")):
            cond_text = " ".join(conditions) if conditions else "See official guidelines."
            parts.append(f"Eligibility details: {cond_text}")

        # Always include summary & application hint if question was general
        if len(parts) == 1:
            parts.append(f"Overview: {scheme.description}")
            parts.append(f"Benefits: {scheme.benefits}")
            if conditions:
                parts.append(f"Key eligibility: {' '.join(conditions)}")
            parts.append(f"Application guidance: {scheme.application_guidance}")

        parts.append(f"Official source: {scheme.source_url} (last reviewed {scheme.last_reviewed})")
        lines.append("\n".join(parts))

    return "\n\n".join(lines)


def _call_llm_if_configured(
    question: str,
    ranked: List[Tuple[Scheme, float]],
    preferred_language: str,
) -> Optional[str]:
    api_key = os.getenv("AI_API_KEY", "").strip()
    if not api_key:
        return None

    api_base = os.getenv("AI_API_BASE", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("AI_MODEL", "gpt-4o-mini")

    context_blocks = []
    for scheme, _ in ranked:
        rules = json.loads(scheme.eligibility_rules_json)
        context_blocks.append(
            f"Scheme: {scheme.name}\n"
            f"Category: {scheme.category}\n"
            f"Description: {scheme.description}\n"
            f"Benefits: {scheme.benefits}\n"
            f"Eligibility Rules: {json.dumps(rules)}\n"
            f"Application Guidance: {scheme.application_guidance}\n"
            f"Source URL: {scheme.source_url} (Reviewed: {scheme.last_reviewed})"
        )

    system_prompt = (
        "You are SAHAAY, a helpful citizen assistant for government welfare schemes. "
        "Answer ONLY using the provided scheme context. Cite the scheme name and source URL. "
        "Do not invent eligibility guarantees or claim official approval. "
        f"Respond clearly in language code '{preferred_language}' (default English if unsure)."
    )
    user_prompt = f"Context:\n{chr(10).join(context_blocks)}\n\nCitizen question: {question}"

    try:
        resp = httpx.post(
            f"{api_base}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
            },
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def answer_question(
    question: str,
    schemes: List[Scheme],
    scheme_slug: Optional[str] = None,
    preferred_language: str = "en",
) -> AssistantResponse:
    """Retrieve matching scheme context and return a grounded AI or extractive answer."""
    ranked = retrieve_relevant_schemes(question, schemes, scheme_slug=scheme_slug)
    citations = [
        CitationOut(
            slug=s.slug,
            name=s.name,
            source_url=s.source_url,
            last_reviewed=s.last_reviewed,
        )
        for s, _ in ranked
    ]

    llm_answer = _call_llm_if_configured(question, ranked, preferred_language)
    if llm_answer:
        return AssistantResponse(
            answer=llm_answer,
            citations=citations,
            mode="rag_llm",
            disclaimer=DISCLAIMER,
        )

    return AssistantResponse(
        answer=_format_grounded_fallback(question, ranked),
        citations=citations,
        mode="rag_extractive",
        disclaimer=DISCLAIMER,
    )
