import builtins

import pytest
from lark import LarkError, Tree

from lox import *
from lox.ast import *


@pytest.fixture
def expr():
    return True


@pytest.fixture
def src():
    return "[1, 2, 3]"


@pytest.fixture
def src_():
    return "[]"


@pytest.fixture
def src__():
    return "[[1], [2 + x], []]"


def test_suporta_listas(cst: Tree, cst_):
    print(pretty := cst.pretty())
    assert "1" in pretty
    assert "2" in pretty
    assert "3" in pretty


def test_suporta_listas_aninhadas(cst__):
    print(pretty := cst__.pretty())
    assert "1" in pretty
    assert "2" in pretty
    assert "x" in pretty


def test_suporta_construção_de_ast(astf, ast_f, ast__f):
    cls = List
    assert isinstance(astf(), cls), "Defina uma classe List em lox/ast.py"
    assert isinstance(ast_f(), cls), "Deve suportar listas vazias"
    assert isinstance(ast__f(), cls), "Deve suportar listas aninhadas"


def test_aceita_vírgula_no_final():
    ast = parse_expr("[1, 2, 3,]")
    result = ast.eval(Ctx())
    assert isinstance(result, list)
    assert result == [1, 2, 3]


@pytest.mark.parametrize("exemplo", ["[,]", "[1,,2]", "[1, 2,,]", "[,1, 2]"])
def test_recusa_listas_inválidas(exemplo):
    with pytest.raises((SyntaxError, LarkError)):
        parse_expr(exemplo)


def test_implementa_a_função_eval(exs):
    def ctx():
        return Ctx.from_dict({"x": 1})

    for ex in exs:
        print(f"Testando {ex.src=}")
        result = ex.ast.eval(ctx())
        expect = builtins.eval(ex.src, {}, ctx())

        assert (
            result == expect
        ), f"[List.eval]: esperava {expect} mas encontrei {result}"
