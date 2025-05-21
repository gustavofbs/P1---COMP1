from pathlib import Path

from lox.aux.re_validator import get_context, reset_context

MOD = Path(__file__).parent.parent / "q1-regex.py"


# def make_tests():
#     for _, value in vars(mod()).items():
#         if test := getattr(value, "run_test", None):
#             yield (test)


# TESTS = [*make_tests()]


def test_question(json_metadata):
    # setup_pytest()
    src = MOD.read_text()
    reset_context()
    exec(src, globals(), ns := {})
    ns.pop("__name__", None)
    ns.pop("__doc__", None)
    ns.pop("__module__", None)
    results = get_context().results
    points = sum(results.values())
    json_metadata["q1"] = {
        "points": points,
        "tests": results,
    }
    assert points == 5, "Obteve menos de 5 points"
