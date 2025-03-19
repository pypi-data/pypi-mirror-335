import logging
from typing import Dict, Union

from odp.tabular_v2.util import exp
from odp.tabular_v2.util.util import FieldNotFound


class MinMax:
    def __init__(self, *vals):
        self.min = None
        self.max = None
        self.nulls = False
        for v in vals:
            self.set(v)

    def set(self, v):
        if v is None:
            self.nulls = True
        elif self.min is None:
            self.min = v
            self.max = v
        elif v is True:
            self.max = True
        elif v is False:
            self.min = False
        else:
            self.min = min(self.min, v)
            self.max = max(self.max, v)
        return self

    def __str__(self):
        return f"mm({self.min}, {self.max}, {self.nulls})"

    def can_be_true(self):
        if self.min is None:
            return False
        if isinstance(self.min, bool):
            return self.max
        if isinstance(self.min, Union[int, float]):
            return self.min != 0 or self.max != 0
        raise NotImplementedError(f"can_be_true not implemented for {self}")

    def can_be_false(self):
        if self.min is None:
            return False
        if isinstance(self.min, bool):
            return self.min is False
        if isinstance(self.min, Union[int, float]):
            if self.min == 0:
                return self.max > 0
            elif self.min < 0:
                return self.max >= 0
            else:
                return False
        raise NotImplementedError(f"can_be_true not implemented for {self}")

    def bin_op(self, op: str, other: "MinMax"):
        out = MinMax()
        out.nulls = self.nulls or other.nulls
        if self.min is None:
            out.min = other.min
            out.max = other.max
            return out
        if other.min is None:
            out.min = self.min
            out.max = self.max
            return out

        def reduce(op):
            for left in self.min, self.max:
                for right in other.min, other.max:
                    try:
                        out.set(op(left, right))
                    except ArithmeticError as e:
                        logging.warning("ArithmeticError: %s %s %s: %s", left, op, right, e)
                        out.set(None)
            return out

        if op == "and":
            if self.can_be_true() and other.can_be_true():
                out.set(True)
            if self.can_be_false() or other.can_be_false():
                out.set(False)
            return out
        if op == "or":
            if self.can_be_true() or other.can_be_true():
                out.set(True)
            if self.can_be_false() and other.can_be_false():
                out.set(False)
            return out

        if op == "+":
            return out.set(self.min + other.min).set(self.max + other.max)
        if op == "-":
            return out.set(self.min - other.max).set(self.max - other.min)
        if op == "*":
            return reduce(lambda a, b: a * b)
        if op == "/":
            return reduce(lambda a, b: a / b)

        if op == "<":
            return reduce(lambda a, b: a < b)
        if op == "<=":
            return reduce(lambda a, b: a <= b)
        if op == ">":
            return reduce(lambda a, b: a > b)
        if op == ">=":
            return reduce(lambda a, b: a >= b)
        if op == "==":
            if self.min <= other.max and self.max >= other.min:
                out.set(True)
            if self.min != self.max or self.min != other.min or self.min != other.max:
                out.set(False)
            return out
        if op == "!=":
            return self.bin_op("==", other).unary_op("not")

        raise NotImplementedError(f"bin op {op} not supported")

    def unary_op(self, op: str):
        if op in ["not", "!", "~"]:
            out = MinMax()
            out.nulls = self.nulls
            if self.can_be_true():
                out.set(False)
            if self.can_be_false():
                out.set(True)
            return out
        raise NotImplementedError(f"unary op {op} not supported")


def minmax(op: exp.Op, row: Dict[str, MinMax]) -> MinMax:
    if isinstance(op, exp.BinOp):
        left = minmax(op.left, row)
        right = minmax(op.right, row)
        return left.bin_op(op.op, right)
    if isinstance(op, exp.UnaryOp):
        return minmax(op.exp, row).unary_op(op.prefix)
    if isinstance(op, exp.Func):
        raise NotImplementedError(f"func {op.name} not supported")
    if isinstance(op, exp.Field):
        try:
            return row[str(op)]
        except KeyError:
            raise FieldNotFound(str(op))
    if isinstance(op, exp.Scalar):
        return MinMax(op.to_py())
    if isinstance(op, exp.Parens):
        return minmax(op.exp, row)
    if isinstance(op, exp.BindVar):
        return MinMax(op.val)
    raise ValueError(f"unexpected op {type(op)}")
