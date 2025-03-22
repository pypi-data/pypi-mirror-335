import numpy as np
from typing import Optional
from .base import ValidationError
from jsonpatch import JsonPatch


class MissingFactors(ValidationError):
    def __init__(self, which_vars: list[str], patch: Optional[JsonPatch] = None):
        super(MissingFactors, self).__init__(
            "Variable(s) '%s' not connected to any factor." % ", ".join(which_vars),
            {"variables": which_vars},
            patch,
        )


class InvalidVariableName(ValidationError):
    def __init__(self, which_var: str, patch: Optional[JsonPatch] = None):
        super(InvalidVariableName, self).__init__(
            "Invalid variable name: '%s'" % which_var,
            {"variable": which_var},
            patch,
        )


class InvalidVariableItemCount(ValidationError):
    def __init__(self, which_var: str, patch: Optional[JsonPatch] = None):
        super(InvalidVariableItemCount, self).__init__(
            "Variable '%s' must have at least 1 value." % which_var,
            {"variable": which_var},
            patch,
        )


class MissingVariable(ValidationError):
    def __init__(self, factor_idx: int, patch: Optional[JsonPatch] = None):
        super(MissingVariable, self).__init__(
            "Factor %d must have at least one variable." % factor_idx,
            {"factor_idx": factor_idx},
            patch,
        )


class MissingProbability(ValidationError):
    def __init__(self, factor_idx: int, patch: Optional[JsonPatch] = None):
        super(MissingProbability, self).__init__(
            "Factor %d must have at least one probability value." % factor_idx,
            {"factor_idx": factor_idx},
            patch,
        )


class VariableMissingInVariableList(ValidationError):
    def __init__(self, which_var: str, patch: Optional[JsonPatch] = None):
        super(VariableMissingInVariableList, self).__init__(
            "Factor variable '%s' is not defined in variables" % which_var,
            {"variable": which_var},
            patch,
        )


class IncorrectTensorShape(ValidationError):
    def __init__(
        self, factor_idx: int, expected_shape: list[int], actual_shape: list[int]
    ):
        super(IncorrectTensorShape, self).__init__(
            "Factor %d 's tensor shape %s is incompatible with its variable cardinalities %s."
            % (factor_idx, actual_shape, expected_shape),
            {
                "factor_idx": factor_idx,
                "expected_shape": expected_shape,
                "actual_shape": actual_shape,
            },
        )


# TODO: 400 - fix VFG to distinguish more clearly between distributions and other tensors,
# so that we know when to apply this. Then need a test
# class StrideMustSumToOneError(ValidationError):
#     def __init__(self, distribution_type: str, val_sum: float, elements: List[str]):
#         super(StrideMustSumToOneError, self).__init__(
#             "Factor values for each category must sum to 1.0 for %s distributions. Found sum of %f for %s"
#             % (distribution_type, val_sum, elements)
#         )


# class InvalidShapeError(ValidationError):
#     def __init__(self, strides: List[int], values: List[float]):
#         super(InvalidShapeError, self).__init__(
#             "Invalid shape. Found strides %s for Values %s; product of strides must equal length of elements"
#             % (strides, values),
#             {"strides": strides, "values": values},
#         )
