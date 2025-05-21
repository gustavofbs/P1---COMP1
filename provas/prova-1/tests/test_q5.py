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
def fib():
    return (Path(__file__).parent.parent / "fib.lox").read_text()


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


def test_fib(fib: str):
    _, fib = fib.split("\n", maxsplit=1)
    ast = parse(fib)

    with redirect_stdout(io.StringIO()) as fd:
        ast.eval(Ctx.from_dict({"n": 10}))
        nums = fd.getvalue().strip().replace("\n", ",")
        expect = "0,1,1,2,3,5,8,13,21,34"
        assert nums == expect

    with redirect_stdout(io.StringIO()) as fd:
        ast.eval(Ctx.from_dict({"n": 15}))
        nums = fd.getvalue().strip().replace("\n", ",")
        expect = "0,1,1,2,3,5,8,13,21,34,55,89,144,233,377"
        assert nums == expect
