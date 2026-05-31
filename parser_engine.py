"""
parser_engine.py
────────────────
NLP pipeline: PDF text extraction, spaCy EntityRuler + Matcher,
keyword scoring, and experience detection.

No external LLM APIs — all processing is local via spaCy.
"""

import re
import spacy
from spacy.cli import download
from spacy.matcher import Matcher
from spacy.language import Language

try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # graceful fallback; error raised at extraction time

from config_manager import generate_keyword_config


# ──────────────────────────────────────────────
# PDF TEXT EXTRACTION
# ──────────────────────────────────────────────
def extract_text_from_pdf(file_obj) -> str:
    """
    Extract plain text from an uploaded binary PDF file object.
    Handles empty pages and normalises whitespace.
    """
    if pdfplumber is None:
        raise ImportError("pdfplumber is required for PDF extraction. Install via: pip install pdfplumber")

    text_parts: list[str] = []
    try:
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as exc:
        raise RuntimeError(f"Failed to read PDF: {exc}") from exc

    raw = "\n".join(text_parts)
    # Collapse excessive whitespace while preserving paragraph breaks
    cleaned = re.sub(r"[ \t]+", " ", raw)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


# ──────────────────────────────────────────────
# spaCy PIPELINE BUILDER
# ──────────────────────────────────────────────
_PIPELINE_CACHE: dict[str, spacy.Language] = {}


def _build_nlp_pipeline(role_name: str, filepath: str | None = None) -> spacy.Language:
    """
    Load en_core_web_sm and prepend an EntityRuler populated with
    keyword patterns for the selected role.
    Pipelines are cached per role to avoid redundant reloads.
    """
    cache_key = f"{role_name}::{filepath}"
    if cache_key in _PIPELINE_CACHE:
        return _PIPELINE_CACHE[cache_key]

    kwargs = {"filepath": filepath} if filepath else {}
    config = generate_keyword_config(role_name, **kwargs)

    # Automatically download the model if missing (fixes Cloud Deployment errors)
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading spaCy model 'en_core_web_sm'...")
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")

    # Add EntityRuler BEFORE the default NER so our rules take priority
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    ruler.add_patterns(config["entity_patterns"])

    # Attach config to the pipeline for easy access later
    nlp.meta["_resume_config"] = config

    _PIPELINE_CACHE[cache_key] = nlp
    return nlp


def clear_pipeline_cache() -> None:
    """Flush the cached pipelines (e.g. after rule changes)."""
    _PIPELINE_CACHE.clear()


# ──────────────────────────────────────────────
# EXPERIENCE MATCHER
# ──────────────────────────────────────────────
def _extract_years_of_experience(nlp: spacy.Language, text: str) -> int | None:
    """
    Use spaCy Matcher to find patterns like:
        '5+ years of experience', '3 yrs experience', '10 years exp'
    Returns the maximum integer found, or None if no match.
    """
    matcher = Matcher(nlp.vocab)

    # Pattern: NUMBER  (+)?  years/yrs  (of)?  experience/exp
    pattern = [
        {"LIKE_NUM": True},
        {"TEXT": "+", "OP": "?"},
        {"LOWER": {"IN": ["years", "yrs", "year"]}},
        {"LOWER": "of", "OP": "?"},
        {"LOWER": {"IN": ["experience", "exp"]}},
    ]
    matcher.add("EXPERIENCE_YEARS", [pattern])

    doc = nlp.make_doc(text)  # tokenise without running full pipeline
    matches = matcher(doc)

    years_found: list[int] = []
    for _, start, _end in matches:
        token_text = doc[start].text
        try:
            years_found.append(int(float(token_text)))
        except (ValueError, TypeError):
            continue

    # Also try regex as a fallback for edge cases
    regex_hits = re.findall(
        r"(\d{1,2})\s*\+?\s*(?:years?|yrs?)[\s\w]*(?:experience|exp)",
        text,
        re.IGNORECASE,
    )
    for hit in regex_hits:
        try:
            years_found.append(int(hit))
        except (ValueError, TypeError):
            continue

    return max(years_found) if years_found else None


# ──────────────────────────────────────────────
# SCORING ENGINE
# ──────────────────────────────────────────────
def score_resume(
    resume_text: str,
    role_name: str,
    filepath: str | None = None,
) -> dict:
    """
    Analyse a single resume against the selected role.
    """
    nlp = _build_nlp_pipeline(role_name, filepath)
    config = nlp.meta["_resume_config"]
    keyword_weights = config["keyword_weights"]
    max_possible = config["max_possible_score"]

    doc = nlp(resume_text.lower())

    # Collect matched skill entities
    skills_found: set[str] = set()

    for ent in doc.ents:
        ent_text = ent.text.strip()
        if ent_text in keyword_weights:
            skills_found.add(ent_text)

    # Also do substring matching for multi-word keywords the ruler might miss
    text_lower = resume_text.lower()
    for keyword in keyword_weights:
        if keyword in text_lower:
            skills_found.add(keyword)

    # Sum up the score of all unique skills found
    total_score = sum(keyword_weights.get(skill, 0) for skill in skills_found)

    favorability = round((total_score / max_possible * 100), 1) if max_possible > 0 else 0.0

    years = _extract_years_of_experience(nlp, resume_text)

    return {
        "total_score": total_score,
        "favorability_pct": min(favorability, 100.0),
        "skills_found": sorted(list(skills_found)),
        "years_of_experience": years,
        "max_possible_score": max_possible,
    }


# ──────────────────────────────────────────────
# BATCH PROCESSOR
# ──────────────────────────────────────────────
def process_resumes(
    files: list,
    role_name: str,
    filepath: str | None = None,
) -> list[dict]:
    """
    Process a batch of uploaded PDF file objects.
    Returns a list of result dicts (one per file).
    """
    results: list[dict] = []

    for f in files:
        file_name = getattr(f, "name", "unknown.pdf")
        try:
            text = extract_text_from_pdf(f)
            if not text.strip():
                results.append({
                    "file_name": file_name,
                    "total_score": 0,
                    "favorability_pct": 0.0,
                    "skills_found": [],
                    "years_of_experience": None,
                    "max_possible_score": 0,
                    "status": "⚠️ Empty — no text extracted",
                })
                continue

            score_data = score_resume(text, role_name, filepath)
            results.append({
                "file_name": file_name,
                **score_data,
                "status": "✅ Processed",
            })
        except Exception as exc:
            results.append({
                "file_name": file_name,
                "total_score": 0,
                "favorability_pct": 0.0,
                "skills_found": [],
                "years_of_experience": None,
                "max_possible_score": 0,
                "status": f"❌ Error: {exc}",
            })

    return results


# ──────────────────────────────────────────────
# Quick self-test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    sample = """
    John Doe — Senior UI/UX Designer
    5+ years of experience in product design.
    Proficient in Figma, wireframing, and user research.
    Experience with Adobe XD, prototyping, and usability testing.
    """
    # Note: For this local test to run without an Excel file, ensure 
    # generate_keyword_config creates mock data if the file is missing.
    result = score_resume(sample, "UI_UX")
    print("Score result:")
    for k, v in result.items():
        print(f"  {k}: {v}")