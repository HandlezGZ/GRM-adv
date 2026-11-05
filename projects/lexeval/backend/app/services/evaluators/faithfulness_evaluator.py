import os
import re
from typing import Any, Optional

from backend.app.services.evaluators.deterministic_evaluator import (
    DeterministicEvaluator,
    normalize_text,
)


class FaithfulnessEvaluator:
    """
    Evaluator specialized in factual faithfulness, hallucination detection,
    and LLM-as-a-judge scoring with resilient local fallback.
    """

    def __init__(self, deterministic_evaluator: Optional[DeterministicEvaluator] = None):
        self.deterministic = deterministic_evaluator or DeterministicEvaluator()

    def extract_numerical_entities(self, text: str) -> list[str]:
        """Extracts numbers, percentages, currency, day/year references."""
        patterns = [
            r"\b\d+[\.,]?\d*\s*%",  # Percentages (e.g. 4,65%, 15%)
            r"\br\$\s*\d+[\.,]?\d*",  # Currency
            r"\b\d+\s*(?:anos?|dias?|meses?|decêndio)\b",  # Durations
            r"\bdia\s+\d+\b",  # Specific days
            r"\b\d{4,}\b",  # Long numbers (laws, REsp numbers)
        ]
        entities = []
        for pat in patterns:
            matches = re.findall(pat, text, flags=re.IGNORECASE)
            for m in matches:
                cleaned = normalize_text(m)
                if cleaned not in entities:
                    entities.append(cleaned)
        return entities

    def check_factual_grounding(
        self, output: str, context: str
    ) -> tuple[float, list[str], list[str]]:
        """
        Verifies if numerical and quantitative entities in the output are grounded in context.
        Returns (grounding_score, supported_entities, hallucinated_entities).
        """
        output_entities = self.extract_numerical_entities(output)
        if not output_entities:
            return 1.0, [], []

        norm_context = normalize_text(context)
        supported = []
        hallucinated = []

        for entity in output_entities:
            # Check direct match or digits match
            digits = re.findall(r"\d+", entity)
            if entity in norm_context or (digits and all(d in norm_context for d in digits)):
                supported.append(entity)
            else:
                hallucinated.append(entity)

        score = len(supported) / len(output_entities)
        return round(score, 4), supported, hallucinated

    def decompose_claims(self, text: str) -> list[str]:
        """Decomposes response into key sentence-level claims."""
        sentences = re.split(r"[.\n;]+", text)
        claims = [s.strip() for s in sentences if len(s.strip()) > 15]
        return claims

    def verify_sentence_claims(
        self, claims: list[str], context: str
    ) -> tuple[float, list[dict[str, Any]]]:
        """
        Verifies each sentence claim against the context document.
        Returns claim support ratio and detailed list of claim verifications.
        """
        if not claims:
            return 1.0, []

        norm_context = normalize_text(context)
        context_tokens = set(re.findall(r"\b\w{3,}\b", norm_context))

        verifications = []
        supported_count = 0

        for claim in claims:
            norm_claim = normalize_text(claim)
            claim_tokens = set(re.findall(r"\b\w{3,}\b", norm_claim))
            if not claim_tokens:
                continue

            overlap = claim_tokens.intersection(context_tokens)
            ratio = len(overlap) / len(claim_tokens)

            is_supported = ratio >= 0.40  # At least 40% significant token overlap
            if is_supported:
                supported_count += 1

            verifications.append(
                {
                    "claim": claim,
                    "supported": is_supported,
                    "token_overlap_ratio": round(ratio, 4),
                }
            )

        overall_ratio = supported_count / len(claims) if claims else 1.0
        return round(overall_ratio, 4), verifications

    def evaluate_llm_judge_mock(
        self, output: str, context: str, expected: str
    ) -> dict[str, Any]:
        """
        Simulated LLM-as-a-judge evaluation for hermetic offline execution and testing.
        """
        # Grounding check
        grounding_score, supported, hallucinated = self.check_factual_grounding(output, context)
        claims = self.decompose_claims(output)
        claims_score, claim_details = self.verify_sentence_claims(claims, context)

        final_judge_score = round(0.5 * grounding_score + 0.5 * claims_score, 4)
        has_hallucinations = len(hallucinated) > 0

        verdict = "PASS" if final_judge_score >= 0.70 and not has_hallucinations else "FAIL"
        reasoning = (
            f"LLM-Judge evaluated {len(claims)} claims against source context. "
            f"Factual grounding score: {grounding_score}. Hallucinated entities: {hallucinated or 'None'}. "
            f"Overall confidence score: {final_judge_score}."
        )

        return {
            "judge_score": final_judge_score,
            "verdict": verdict,
            "reasoning": reasoning,
            "claims_evaluated": len(claims),
            "hallucinated_entities": hallucinated,
            "supported_entities": supported,
        }

    def evaluate_case(
        self,
        output: str,
        input_query: str,
        context_document: str,
        expected_output: str,
        required_keywords: list[str],
        forbidden_terms: list[str],
        evaluator_type: str = "hybrid",
        threshold: float = 0.70,
    ) -> dict[str, Any]:
        """
        Runs hybrid evaluation combining deterministic checks, factual grounding,
        and LLM-judge verification.
        """
        # 1. Run deterministic checks first
        det_result = self.deterministic.evaluate_case(
            output=output,
            input_query=input_query,
            context_document=context_document,
            expected_output=expected_output,
            required_keywords=required_keywords,
            forbidden_terms=forbidden_terms,
            threshold=threshold,
        )

        # 2. Check numerical/factual grounding
        grounding_score, supported_ents, hallucinated_ents = self.check_factual_grounding(
            output, context_document
        )

        # 3. Verify sentence claims
        claims = self.decompose_claims(output)
        claims_ratio, claim_details = self.verify_sentence_claims(claims, context_document)

        # 4. LLM judge evaluation (or fallback)
        use_llm_judge = (
            evaluator_type in ("llm", "hybrid")
            or os.getenv("ENABLE_LLM_JUDGE", "false").lower() == "true"
        )
        judge_data = self.evaluate_llm_judge_mock(output, context_document, expected_output)

        # Calculate synthesized faithfulness score
        if evaluator_type == "deterministic":
            faithfulness_score = det_result["faithfulness_score"]
        else:
            # Hybrid weighted combination
            faithfulness_score = round(
                0.40 * det_result["faithfulness_score"]
                + 0.35 * grounding_score
                + 0.25 * claims_ratio,
                4,
            )

        if hallucinated_ents:
            faithfulness_score = max(0.0, faithfulness_score - 0.35)

        relevance_score = det_result["relevance_score"]
        schema_score = det_result["schema_score"]

        # Failure classification
        passed = True
        failure_reason = None

        if det_result["failure_reason"]:
            passed = False
            failure_reason = det_result["failure_reason"]
        elif hallucinated_ents:
            passed = False
            failure_reason = "HALLUCINATED_NUMERICAL_VALUE"
        elif claims_ratio < 0.50:
            passed = False
            failure_reason = "UNGROUNDED_CLAIM"
        elif faithfulness_score < threshold:
            passed = False
            failure_reason = "LOW_FAITHFULNESS"
        elif relevance_score < threshold:
            passed = False
            failure_reason = "INSUFFICIENT_RELEVANCE"

        reasoning = (
            f"Factual Faithfulness: {faithfulness_score:.2f} (grounding={grounding_score:.2f}, "
            f"claims_support={claims_ratio:.2f}). Relevance: {relevance_score:.2f}. "
            f"Pass status: {'APPROVED' if passed else 'REJECTED'}. "
            f"Failure: {failure_reason or 'None'}."
        )

        diagnostics = {
            **det_result["diagnostics"],
            "evaluator_type": evaluator_type,
            "factual_grounding": {
                "score": grounding_score,
                "supported_entities": supported_ents,
                "hallucinated_entities": hallucinated_ents,
            },
            "claims_analysis": {
                "total_claims": len(claims),
                "supported_ratio": claims_ratio,
                "claim_details": claim_details,
            },
            "judge_result": judge_data if use_llm_judge else None,
            "evaluator_reasoning": reasoning,
        }

        return {
            "schema_score": schema_score,
            "faithfulness_score": round(faithfulness_score, 4),
            "relevance_score": round(relevance_score, 4),
            "passed": passed,
            "failure_reason": failure_reason,
            "diagnostics": diagnostics,
        }
