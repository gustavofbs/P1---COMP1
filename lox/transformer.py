#​ Edite a  classe​ ​LoxTransformer​ ​nesse ​arquivo.​ ​Boa​ prova!
"""
Implementa o transformador da árvore sintática que converte entre as representações

    lark.Tree -> lox.ast.Node.

A resolução de vários exercícios requer a modificação ou implementação de vários
métodos desta classe.
"""

from typing import Callable

from lark import Transformer, v_args

from . import runtime as op
from .ast import *


def op_handler(op: Callable):
    """
    Fábrica de métodos que lidam com operações binárias na árvore sintática.

    Recebe a função que implementa a operação em tempo de execução.
    """

    def method(self, left, right):
        return BinOp(left, right, op)

    return method


@v_args(inline=True)
class LoxTransformer(Transformer):
    # Programa
    def program(self, *stmts):
        return Program(list(stmts))

    # Operações matemáticas básicas
    mul = op_handler(op.mul)
    div = op_handler(op.truediv)
    sub = op_handler(op.sub)
    add = op_handler(op.add)

    # Comparações
    gt = op_handler(op.gt)
    lt = op_handler(op.lt)
    ge = op_handler(op.ge)
    le = op_handler(op.le)
    eq = op_handler(op.eq)
    ne = op_handler(op.ne)

    def not_(self, expr):
        return UnaryOp(op.not_, expr)

    def neg(self, expr):
        return UnaryOp(op.neg, expr)

    # Outras expressões
    def func_call(self, name: Var, params: list):
        return Call(name.name, params)

    def params(self, *args):
        params = list(args)
        return params

    def assign(self, name: Var, value: Expr):
        return Assign(name.name, value)

    # Comandos
    def var_def(self, name: Var, expr: Expr | None = None):
        return VarDef(name.name, expr)

    def print_cmd(self, expr):
        return Print(expr)

    def block(self, *stmts: Stmt):
        return Block(list(stmts))
        
    def while_cmd(self, condition: Expr, body: Stmt):
        return While(condition, body)
        
    def if_cmd(self, condition: Expr, then_branch: Stmt, else_branch: Stmt = None):
        return If(condition, then_branch, else_branch)

    def VAR(self, token):
        name = str(token)
        return Var(name)

    def NUMBER(self, token):
        num = float(token)
        return Literal(num)

    def STRING(self, token):
        text = str(token)[1:-1]
        return Literal(text)

    def NIL(self, _):
        return Literal(None)

    def BOOL(self, token):
        return Literal(token == "true")
        
    def list(self, items=None):
        if items is None:
            items = []
        return List(items)
        
    def list_items(self, *items):
        return list(items)
