
from agentes.coder import CoderAI
from agentes.reviewer import Reviewer
from agentes.tester import TesterAI


def test_pipeline_happy_path():
    coder = CoderAI()
    reviewer = Reviewer()
    tester = TesterAI()

    spec = "Retornar OK para a chamada principal"
    code_result = coder.handle(spec)
    assert "code" in code_result

    review = reviewer.handle({"code": code_result["code"]})
    assert review.get("ok") is True

    test_res = tester.handle({"code": code_result["code"]})
    assert test_res.get("ok") is True


def test_pipeline_syntax_error():
    coder = CoderAI()
    reviewer = Reviewer()
    tester = TesterAI()

    # simulate broken code
    bad_code = "def ()\n    pass"
    review = reviewer.handle({"code": bad_code})
    assert review.get("ok") is False
