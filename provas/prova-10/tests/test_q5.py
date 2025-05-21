import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from lox import *
from lox.ast import *


@pytest.fixture
def expr():
    return False


@pytest.fixture
def maior():
    return (Path(__file__).parent.parent / "maior.lox").read_text()


@pytest.fixture
def src():
    return 'while (cond()) print "a";'


@pytest.fixture
def src_():
    return 'while (cond()) {print "a"; print "b";}'


@pytest.fixture
def src__():
    return 'while (cond1()) while (cond2()) { print "a"; }'


def test_implementa_a_função_eval(exs: list):
    def ctx():
        return {
            "cond": iter([True, True, False]).__next__,
            "cond1": iter([True, True, False]).__next__,
            "cond2": iter([True, True, True, False] * 2).__next__,
        }

    prints = ["a\n" * 2, "a\nb\n" * 2, "a\n" * 6]
    for expected, ex in zip(prints, exs):
        print(f"Testando {ex.src=}")
        with redirect_stdout(io.StringIO()) as fd:
            ex.ast.eval(ctx())

        printed = fd.getvalue()
        assert (
            printed == expected
        ), f"{ex.src=}, Esperava imprimir {expected!r} mas obteve {printed!r}"


def test_laços_infinitos():
    for src in [
        'while (0) { f(); print "step"; }',
        'while ("") { f(); print "step"; }',
    ]:
        n = 10

        def f():
            nonlocal n
            n -= 1
            if n <= 0:
                raise StopIteration

        with pytest.raises(StopIteration):
            eval(src, Ctx.from_dict({"f": f}))
            if n == 10:
                raise AssertionError(f"não entrou no loop infinito: {src}")
            assert n == 0


def test_termina_laço_quando_a_condição_é_falsa(ex):
    print(f"{ex.src=}")

    outs = iter([True, True, True, False])
    n = 0

    def cond():
        nonlocal n
        n += 1
        return next(outs)

    with redirect_stdout(io.StringIO()) as fd:
        ex.ast.eval(Ctx.from_dict({"cond": cond}))

    assert n == 4, f"Esperava que a condição fosse chamada 4 vezes, mas foi {n}"

    printed = fd.getvalue()
    assert printed == "a\na\na\n"


def test_maior(maior: str):
    _, _, maior = maior.split("\n", maxsplit=2)
    ast = parse(maior)

    with redirect_stdout(io.StringIO()) as fd:
        ast.eval(Ctx.from_dict({"a": 1, "b": 2}))
        nums = fd.getvalue().strip().replace("\n", ",")
        expect = "maior: b"
        assert nums == expect

    with redirect_stdout(io.StringIO()) as fd:
        ast.eval(Ctx.from_dict({"a": 10, "b": 1}))
        nums = fd.getvalue().strip().replace("\n", ",")
        expect = "maior: a"
        assert nums == expect
