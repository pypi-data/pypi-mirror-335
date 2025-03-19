import numba
import numpy as np

from chrono_features.features.base import _FromNumbaFunc
from chrono_features.window_type import WindowType


class Std(_FromNumbaFunc):
    def __init__(self, column: str, window_type: WindowType, out_column_name=None):
        super().__init__(column, window_type, out_column_name)
        self.out_column_name = (
            out_column_name or f"{self.column}_std_{window_type.suffix}"
        )

    @staticmethod
    @numba.njit
    def _numba_func(xs: np.array):
        return np.std(xs)
