from abc import ABC, abstractmethod
from typing import Callable

import numba
import numpy as np
import polars as pl

from chrono_features.ts_dataset import TSDataset
from chrono_features.window_type import WindowType


@numba.jit(nopython=True)
def _calculate_expanding_window_length(ids: np.ndarray) -> np.ndarray:
    lens = np.empty(len(ids), dtype=np.int32)
    lens[0] = 1
    for i in range(1, len(lens)):
        if ids[i] == ids[i - 1]:
            lens[i] = lens[i - 1] + 1
        else:
            lens[i] = 1
    return lens


@numba.jit(nopython=True)
def _calculate_rolling_window_length(
    ids: np.ndarray,
    window_size: int,
    only_full_window: bool
) -> np.ndarray:
    lens = np.empty(len(ids), dtype=np.int32)
    lens[0] = 1
    for i in range(1, len(lens)):
        if ids[i] == ids[i - 1]:
            lens[i] = lens[i - 1] + 1
        else:
            lens[i] = 1

    if only_full_window:
        for i in range(len(lens)):
            if lens[i] >= window_size:
                lens[i] = window_size
            else:
                lens[i] = 0
    else:
        for i in range(len(lens)):
            if lens[i] > window_size:
                lens[i] = window_size

    return lens


class FeatureGenerator(ABC):
    def __init__(self, column: str, window_type: WindowType, out_column_name=None):
        self.column = column
        self.generate_type = window_type
        self.out_column_name = out_column_name

    def calculate_len(self, dataset: TSDataset) -> np.ndarray:
        if isinstance(self.generate_type, WindowType.DYNAMIC):
            return dataset.data[self.generate_type.len_column_name].to_numpy()

        ids = dataset.data[dataset.id_column_name].hash().to_numpy()

        # Вызов оптимизированной функции для расчета длины окон
        if self.generate_type == WindowType.EXPANDING:
            lens = _calculate_expanding_window_length(ids)
        elif isinstance(self.generate_type, WindowType.ROLLING):
            window_size = self.generate_type.size
            only_full_window = self.generate_type.only_full_window
            lens = _calculate_rolling_window_length(ids, window_size, only_full_window)
        else:
            raise ValueError(f"Unsupported generate_type: {self.generate_type}")

        return lens

    @abstractmethod
    def generate(self, dataset: TSDataset) -> np.ndarray:
        raise NotImplementedError


class _FromNumbaFunc(FeatureGenerator):
    @staticmethod
    @numba.njit
    def apply_func_to_full_window(
        feature: np.ndarray, func: Callable, lens: np.array
    ) -> np.ndarray:
        result = np.empty(len(feature), dtype=np.float32)
        for i in numba.prange(len(result)):
            if lens[i]:
                result[i] = func(feature[i + 1 - lens[i] : i + 1])
            else:
                result[i] = np.nan
        return result

    @abstractmethod
    @numba.njit
    def _numba_func(xs: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def generate(self, dataset: TSDataset):
        lens = self.calculate_len(dataset)
        dataset.data = dataset.data.with_columns(
            pl.Series(
                _FromNumbaFunc.apply_func_to_full_window(
                    dataset.data[self.column].to_numpy(),
                    func=self._numba_func,
                    lens=lens,
                )
            ).alias(self.out_column_name)
        )
        return dataset
