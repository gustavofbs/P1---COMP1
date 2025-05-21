from typing import Any

import pytest
from lark import Tree

from lox import *
from lox.ast import *


@pytest.fixture
def expr():
    return False


@pytest.fixture
def src():
    return 'while (cond()) print "a";'


@pytest.fixture
def src_():
    return 'while (cond()) {print "a"; print "b";}'


@pytest.fixture
def src__():
    return 'while (cond1()) while (cond2()) { print "a"; }'


def test_suporta_if_then_else(cst: Tree):
    print(pretty := cst.pretty())
    assert "cond" in pretty
    assert "a" in pretty


def test_suporta_if_then(cst_: Tree):
    print(pretty := cst_.pretty())
    assert "cond" in pretty
    assert "a" in pretty
    assert "b" in pretty


def test_suporta_ifs_aninhados(cst__: Tree):
    print(pretty := cst__.pretty())
    assert "cond1" in pretty
    assert "cond2" in pretty
    assert "a" in pretty


def test_suporta_construção_de_ast(
    astf: Callable[[], Any], ast_f: Callable[[], Any], ast__f: Callable[[], Any]
):
    cls = While
    assert isinstance(astf(), cls), "Deve suportar while com expressão simples"
    assert isinstance(ast_f(), cls), "Deve suportar while com bloco de instruções"
    assert isinstance(ast__f(), cls), "While pode estar aninhado em outro while"


def test_guarda_filhos_corretamente(ast_: Node):
    cmd1 = Print(Literal("a"))
    cmd2 = Print(Literal("b"))
    assert cmd1 not in ast_.children(), "deve guardar múltiplos filhos em um bloco"

    descendants = list(ast_.descendants())
    assert (
        cmd1 in descendants and cmd2 in descendants
    ), 'esperava encontrar os comandos print "a" e print "b"'
