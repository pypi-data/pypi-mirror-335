from typing import Optional
from .base import ModelTypeError
from .bayes_net import InvalidFactorRole
from jsonpatch import JsonPatch


class ConditionalDistributionInMRF(ModelTypeError):
    def __init__(self, factor_idx: int, patch: Optional[JsonPatch] = None):
        super(ConditionalDistributionInMRF, self).__init__(
            "Factor %d represents a conditional distribution. Markov random fields use symmetric potential functions (categorical distributions)."
            % factor_idx,
            {"factor_idx": factor_idx},
            patch,
        )
