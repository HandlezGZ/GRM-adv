import json
import re
import unicodedata
from typing import Any, Optional


def normalize_text(text: str) -> str:
    """Normalize text by lowering, removing extra spaces and normalizing unicode."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text.lower().strip())


class DeterministicEvaluator:
    """
    Evaluator performing rule-based, lexical, and constraint validations:
    - Schema compliance (JSON parsing & field verification if JSON is expected)
    - Required keywords presence
    - Forbidden negative constraints detection
    - Citation extraction and grounding in context
    - Token overlap / lexical similarity against ground truth
    """

    CITATION_PATTERNS = [
        r"\b(?:lei(?:\s+complementar)?|lc)\s+(?:n[ºo°]\s*)?[\d\.\/]+",
        r"\bart(?:igo)?\.?\s+\d+[ºo°]?(?:,\s*inciso\s+[ivxlcdm]+)?(?:\s+(?:do|da)\s+[a-z]+)?",
        r"\btema\s+(?:n[ºo°]\s*)?\d+(?:\/[a-z]{2,4})?",
        r"\b(?:resp|re|adi|adc|adpf)\s+(?:n[ºo°]\s*)?[\d\.\/]+(?:(?:\/[a-z]{2})?)",
        r"\bs[úu]mula\s+(?:vinculante\s+)?(?:n[ºo°]\s*)?\d+",
    ]

    def check_schema_compliance(
        self, text: str, required_keys: Optional[list[str]] = None
    ) -> tuple[float, dict[str, Any]]:
        """Checks if text contains valid JSON and matches required keys if required."""
        text_trimmed = text.strip()
        # If output attempts to be JSON (starts with { or [)
        if text_trimmed.startswith("{") or text_trimmed.startswith("["):
            try:
                parsed = json.loads(text_trimmed)
                if required_keys and isinstance(parsed, dict):
                    missing_keys = [k for k in required_keys if k not in parsed]
                    if missing_keys:
                        return 0.5, {"valid_json": True, "missing_keys": missing_keys}
                return 1.0, {"valid_json": True, "is_json": True}
            except Exception as e:
                return 0.0, {"valid_json": False, "error": str(e)}

        # If plain text was provided, schema compliance is valid (1.0)
        return 1.0, {"valid_json": None, "format": "text"}

    def check_required_keywords(
        self, text: str, required_keywords: list[str]
    ) -> tuple[float, list[str], list[str]]:
        """Calculates presence of required keywords in the generated response."""
        if not required_keywords:
            return 1.0, [], []

        norm_text = normalize_text(text)
        found = []
        missing = []

        for kw in required_keywords:
            norm_kw = normalize_text(kw)
            if norm_kw in norm_text:
                found.append(kw)
            else:
                missing.append(kw)

        score = len(found) / len(required_keywords)
        return round(score, 4), found, missing

    def check_forbidden_terms(
        self, text: str, forbidden_terms: list[str]
    ) -> tuple[bool, list[str]]:
        """Detects presence of forbidden terms or guardrail violations."""
        if not forbidden_terms:
            return False, []

        norm_text = normalize_text(text)
        found = []
        for ft in forbidden_terms:
            norm_ft = normalize_text(ft)
            if norm_ft in norm_text:
                found.append(ft)

        has_violation = len(found) > 0
        return has_violation, found

    def extract_citations(self, text: str) -> list[str]:
        """Extracts specific legal citations (laws, articles, themes, court decisions) from text."""
        citations = []
        for pattern in self.CITATION_PATTERNS:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            for m in matches:
                normalized = re.sub(r"\s+", " ", m.strip())
                if normalized.lower() not in [c.lower() for c in citations]:
                    citations.append(normalized)
        return citations

    def check_citation_precision(
        self, output: str, context: str
    ) -> tuple[float, list[str], list[str]]:
        """
        Extracts citations from output and checks whether each exists in context.
        Returns (precision_score, valid_citations, ungrounded_citations).
        """
        output_citations = self.extract_citations(output)
        if not output_citations:
            return 1.0, [], []

        norm_context = normalize_text(context)
        valid = []
        ungrounded = []

        for cit in output_citations:
            norm_cit = normalize_text(cit)
            # Match numbers or main identifiers in citation
            numbers = re.findall(r"\d+", norm_cit)
            found_in_context = norm_cit in norm_context
            if not found_in_context and numbers:
                # check if the core numbers (e.g. 174 or 10.833) appear in context
                found_in_context = all(num in norm_context for num in numbers)

            if found_in_context:
                valid.append(cit)
            else:
                ungrounded.append(cit)

        precision = len(valid) / len(output_citations)
        return round(precision, 4), valid, ungrounded

    def calculate_lexical_similarity(self, output: str, expected: str) -> float:
        """Calculates token-level F1 overlap between output and ground truth."""
        norm_output = normalize_text(output)
        norm_expected = normalize_text(expected)

        tokens_out = set(re.findall(r"\b\w{3,}\b", norm_output))
        tokens_exp = set(re.findall(r"\b\w{3,}\b", norm_expected))

        if not tokens_out or not tokens_exp:
            return 0.0

        common = tokens_out.intersection(tokens_exp)
        precision = len(common) / len(tokens_out)
        recall = len(common) / len(tokens_exp)

        if precision + recall == 0:
            return 0.0

        f1 = 2 * (precision * recall) / (precision + recall)
        return round(f1, 4)

    def evaluate_case(
        self,
        output: str,
        input_query: str,
        context_document: str,
        expected_output: str,
        required_keywords: list[str],
        forbidden_terms: list[str],
        threshold: float = 0.70,
    ) -> dict[str, Any]:
        """Runs the deterministic suite on a single test case."""
        # 1. Schema check
        schema_score, schema_diag = self.check_schema_compliance(output)

        # 2. Keywords check
        kw_score, kw_found, kw_missing = self.check_required_keywords(output, required_keywords)

        # 3. Forbidden terms
        violated_forbidden, found_forbidden = self.check_forbidden_terms(output, forbidden_terms)

        # 4. Citation precision
        cit_score, valid_cits, ungrounded_cits = self.check_citation_precision(
            output, context_document
        )

        # 5. Lexical overlap against ground truth
        lex_sim = self.calculate_lexical_similarity(output, expected_output)

        # Faithfulness score: citation precision penalized if forbidden terms are found
        faithfulness_score = cit_score
        if violated_forbidden:
            faithfulness_score = max(0.0, faithfulness_score - 0.5)

        # Relevance score: combination of keywords found and lexical similarity
        relevance_score = round(0.6 * kw_score + 0.4 * min(1.0, lex_sim * 1.5), 4)

        # Determine pass/fail & failure reason
        passed = True
        failure_reason = None

        if schema_score < 1.0 and schema_diag.get("valid_json") is False:
            passed = False
            failure_reason = "SCHEMA_ERROR"
        elif violated_forbidden:
            passed = False
            failure_reason = "FORBIDDEN_TERM_VIOLATION"
        elif ungrounded_cits:
            passed = False
            failure_reason = "HALLUCINATED_CITATION"
        elif faithfulness_score < threshold:
            passed = False
            failure_reason = "LOW_FAITHFULNESS"
        elif relevance_score < threshold:
            passed = False
            failure_reason = "INSUFFICIENT_RELEVANCE"

        diagnostics = {
            "evaluator": "deterministic",
            "schema": schema_diag,
            "keywords": {
                "score": kw_score,
                "found": kw_found,
                "missing": kw_missing,
            },
            "forbidden": {
                "violated": violated_forbidden,
                "found": found_forbidden,
            },
            "citations": {
                "precision": cit_score,
                "valid": valid_cits,
                "ungrounded": ungrounded_cits,
            },
            "lexical_similarity": lex_sim,
        }

        return {
            "schema_score": schema_score,
            "faithfulness_score": round(faithfulness_score, 4),
            "relevance_score": round(relevance_score, 4),
            "passed": passed,
            "failure_reason": failure_reason,
            "diagnostics": diagnostics,
        }
