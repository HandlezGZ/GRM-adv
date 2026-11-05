from backend.app.services.evaluators.deterministic_evaluator import DeterministicEvaluator


def test_schema_compliance_valid_and_invalid():
    evaluator = DeterministicEvaluator()

    # Plain text returns 1.0
    score, diag = evaluator.check_schema_compliance("This is regular plain text response.")
    assert score == 1.0
    assert diag["format"] == "text"

    # Valid JSON
    score, diag = evaluator.check_schema_compliance('{"answer": "yes", "article": 138}')
    assert score == 1.0
    assert diag["valid_json"] is True

    # Invalid JSON
    score, diag = evaluator.check_schema_compliance('{"answer": "yes", broken_json')
    assert score == 0.0
    assert diag["valid_json"] is False


def test_required_keywords_check():
    evaluator = DeterministicEvaluator()
    keywords = ["PIS", "COFINS", "Tema 779", "STJ"]

    text_all = "O STJ, no Tema 779, julgou os créditos de PIS e COFINS."
    score, found, missing = evaluator.check_required_keywords(text_all, keywords)
    assert score == 1.0
    assert len(found) == 4
    assert len(missing) == 0

    text_partial = "Decisão referente a PIS e COFINS sem citar precedentes."
    score_p, found_p, missing_p = evaluator.check_required_keywords(text_partial, keywords)
    assert score_p == 0.5
    assert "Tema 779" in missing_p


def test_forbidden_terms_detection():
    evaluator = DeterministicEvaluator()
    forbidden = ["vedado o crédito", "impossível creditar"]

    safe_text = "O crédito é perfeitamente admitido nos termos da jurisprudência."
    violation, found = evaluator.check_forbidden_terms(safe_text, forbidden)
    assert not violation
    assert len(found) == 0

    bad_text = "Conclui-se que é vedado o crédito de PIS em qualquer hipótese."
    violation, found = evaluator.check_forbidden_terms(bad_text, forbidden)
    assert violation
    assert "vedado o crédito" in found


def test_citation_precision_and_grounding():
    evaluator = DeterministicEvaluator()
    context = (
        "Conforme art. 138 do CTN e Súmula 360 do STJ, a denúncia espontânea "
        "afasta a multa punitiva e moratória."
    )

    # Valid citations matching context
    good_output = "Nos termos do art. 138 do CTN e Súmula 360, a multa é excluída."
    prec, valid, ungrounded = evaluator.check_citation_precision(good_output, context)
    assert prec == 1.0
    assert len(ungrounded) == 0
    assert len(valid) >= 1

    # Hallucinated citation not in context
    bad_output = "Conforme o art. 999 da Lei 9.999/99, a dívida foi cancelada."
    prec_bad, valid_bad, ungrounded_bad = evaluator.check_citation_precision(bad_output, context)
    assert prec_bad == 0.0
    assert len(ungrounded_bad) >= 1


def test_evaluate_case_full_flow():
    evaluator = DeterministicEvaluator()
    context = "O art. 174 do CTN estabelece prazo prescricional de 5 anos para a cobrança."
    expected = "O prazo de prescrição é de 5 anos conforme art. 174 do CTN."
    required_keywords = ["5 anos", "art. 174", "prescricional"]
    forbidden_terms = ["10 anos", "20 anos"]

    # Passing case
    pass_res = evaluator.evaluate_case(
        output="O prazo prescricional do art. 174 do CTN é de 5 anos para a Fazenda.",
        input_query="Qual o prazo?",
        context_document=context,
        expected_output=expected,
        required_keywords=required_keywords,
        forbidden_terms=forbidden_terms,
    )
    assert pass_res["passed"] is True
    assert pass_res["failure_reason"] is None
    assert pass_res["faithfulness_score"] == 1.0

    # Failing case due to hallucinated citation
    fail_res = evaluator.evaluate_case(
        output="O prazo do art. 999 da Lei 9.999 é de 5 anos.",
        input_query="Qual o prazo?",
        context_document=context,
        expected_output=expected,
        required_keywords=required_keywords,
        forbidden_terms=forbidden_terms,
    )
    assert fail_res["passed"] is False
    assert fail_res["failure_reason"] == "HALLUCINATED_CITATION"
