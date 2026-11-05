from backend.app.services.evaluators.faithfulness_evaluator import FaithfulnessEvaluator


def test_factual_grounding_exact_match():
    evaluator = FaithfulnessEvaluator()
    context = (
        "A retenção da CSRF de 4,65% deve ser recolhida até o dia 20 do mês subsequente."
    )
    output = "O valor devido de 4,65% deve ser pago até o dia 20."

    score, supported, hallucinated = evaluator.check_factual_grounding(output, context)
    assert score == 1.0
    assert "4,65%" in supported
    assert "dia 20" in supported
    assert len(hallucinated) == 0


def test_factual_grounding_hallucinated_values():
    evaluator = FaithfulnessEvaluator()
    context = (
        "A retenção da CSRF de 4,65% deve ser recolhida até o dia 20 do mês subsequente."
    )
    # Output invents 15% and dia 10
    output = "A retenção é de 15% e o prazo é dia 10."

    score, supported, hallucinated = evaluator.check_factual_grounding(output, context)
    assert score == 0.0
    assert "15%" in hallucinated
    assert "dia 10" in hallucinated


def test_claim_decomposition_and_verification():
    evaluator = FaithfulnessEvaluator()
    context = (
        "Conforme art. 174 do CTN, a prescrição ocorre em 5 anos a contar da constituição definitiva."
    )
    claims = [
        "A prescrição ocorre em 5 anos nos termos do art. 174 do CTN.",
        "Existe isenção automática para todas as pessoas físicas em processo criminal.",
    ]
    ratio, details = evaluator.verify_sentence_claims(claims, context)
    assert len(details) == 2
    assert details[0]["supported"] is True
    assert details[1]["supported"] is False
    assert ratio == 0.5


def test_llm_judge_mock():
    evaluator = FaithfulnessEvaluator()
    context = "O ITCMD não incide sobre planos de previdência VGBL conforme o STJ."
    output = "O STJ consolidou que o ITCMD não incide sobre VGBL."

    judge_res = evaluator.evaluate_llm_judge_mock(output, context, output)
    assert judge_res["verdict"] == "PASS"
    assert judge_res["judge_score"] >= 0.70
    assert "LLM-Judge" in judge_res["reasoning"]


def test_evaluate_case_catches_hallucination():
    evaluator = FaithfulnessEvaluator()
    context = (
        "Nos termos do art. 17 da LC 123/2006, empresas com débitos fiscais podem ser excluídas "
        "do Simples Nacional se não regularizarem em 30 dias."
    )
    expected = "Empresas com dívidas são excluídas do Simples em 30 dias."

    # Hallucinating 90 dias instead of 30 dias
    bad_output = (
        "A exclusão do Simples Nacional ocorre no prazo de 90 dias segundo a LC 123/2006."
    )

    result = evaluator.evaluate_case(
        output=bad_output,
        input_query="Qual o prazo?",
        context_document=context,
        expected_output=expected,
        required_keywords=["LC 123/2006", "Simples Nacional"],
        forbidden_terms=[],
        evaluator_type="hybrid",
    )

    assert result["passed"] is False
    assert result["failure_reason"] == "HALLUCINATED_NUMERICAL_VALUE"
    assert "evaluator_reasoning" in result["diagnostics"]
