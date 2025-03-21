"""
Transformation pass to rewrite in-place tuple mutation as functional updates.
"""

from typing import Optional

from .define_use import DefineUse
from .ssa import SSA
from .verify import VerifyIR
from ..ir import *

class _FuncUpdateInstance(DefaultTransformVisitor):
    """Single-use instance of the FuncUpdate pass."""
    func: FunctionDef

    def __init__(self, func: FunctionDef):
        self.func = func

    def apply(self) -> FunctionDef:
        return self._visit_function(self.func, None)

    def _visit_ref_assign(self, stmt: RefAssign, ctx: None):
        slices = [self._visit_expr(slice, ctx) for slice in stmt.slices]
        expr = self._visit_expr(stmt.expr, ctx)
        e = TupleSet(Var(stmt.var), slices, expr)
        return VarAssign(stmt.var, AnyType(), e), None

class FuncUpdate:
    """
    Transformation pass to rewrite in-place tuple mutation as functional updates.

    This pass rewrites the IR to use functional updates instead of
    in-place tuple mutation. While variables may still be mutated by
    re-assignment, this transformation ensures that no tuple is mutated.
    """

    @staticmethod
    def apply(func: FunctionDef, names: Optional[set[str]] = None) -> FunctionDef:
        if names is None:
            uses = DefineUse.analyze(func)
            names = set(uses.keys())
        ir = _FuncUpdateInstance(func).apply()
        ir = SSA.apply(ir)
        VerifyIR.check(ir)
        return ir
