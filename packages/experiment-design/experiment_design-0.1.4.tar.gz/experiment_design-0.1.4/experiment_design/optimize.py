import logging
import warnings
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from scipy.special import comb as combine

from experiment_design.scorers import Scorer


def random_search(
    creator: Callable[[], np.ndarray], scorer: Scorer, steps: int
) -> np.ndarray:
    """
    Given a |DoE| creator and scorer, maximize the score by random search.

    :param creator: |DoE| creating function.
    :param scorer: |DoE| scoring function.
    :param steps: Number of steps to search.
    :return: The |DoE| matrix with the best score.
    """
    steps = max(1, steps)
    best_doe = creator()
    start_score = best_score = scorer(best_doe)
    logging.debug(f"Initial score: {start_score:.2e}")
    for i_try in range(2, steps + 1):
        doe = creator()
        score = scorer(doe)
        if score > best_score:
            best_doe = doe
            best_score = score
            logging.debug(
                f"Step {i_try} - start score improved by {100 * abs((best_score - start_score) / start_score):.1f}%"
            )
    logging.info(
        f"Final score improved start score by {100 * abs((best_score - start_score) / start_score):.1f}% in {steps} steps"
    )
    return best_doe


def simulated_annealing_by_perturbation(
    doe: np.ndarray,
    scorer: Scorer,
    steps: int = 1000,
    cooling_rate: float = 0.95,
    temperature: float = 25.0,
    max_steps_without_improvement: int = 25,
) -> np.ndarray:
    """
    Simulated annealing algorithm to maximize the score of a |DoE| by
    perturbing the rows of the design matrix along the columns. This kind of perturbation is
    used to avoid violating the |LHS|, i.e. to keep the number of filled bins
    same.

    :param doe: |DoE| matrix with shape (sample_size, len(variables)).
    :param scorer: Scoring function for the doe. It will be maximized.
    :param steps: Number of steps for the annealing algorithm.
    :param cooling_rate: Annealing parameter to decay temperature.
    :param temperature: Annealing temperature.
    :param max_steps_without_improvement: Limit on the maximum steps to take for exploration before setting the
        reference matrix to the last best value.
    :return: Optimized |DoE| matrix

    References
    ----------
    R.V. Joseph and Y. Hung (2008). "`Orthogonal-Maximin Latin Hypercube Designs
    <https://www3.stat.sinica.edu.tw/statistica/oldpdf/A18n17.pdf>`_"

    C. Bogoclu (2022). "`Local Latin Hypercube Refinement for Uncertainty Quantification and Optimization
    <https://hss-opus.ub.ruhr-uni-bochum.de/opus4/frontdoor/deliver/index/docId/9143/file/diss.pdf>`_" Chapter 4.3.2.2

    """
    if temperature <= 1e-16:
        raise ValueError("temperature must be strictly positive.")
    if not 0 <= cooling_rate <= 1:
        raise ValueError("decay has to be between 0 and 1.")

    def cool_down_temperature(temp: float, min_temperature: float = 1e-6) -> float:
        return max(temp * cooling_rate, min_temperature)

    if max_steps_without_improvement < 1:
        max_steps_without_improvement = 1

    doe_start = doe.copy()
    best_doe = doe.copy()
    start_score = anneal_step_score = best_score = scorer(doe)
    logging.debug(f"Initial score: {start_score:.2e}")
    steps_without_improvement = 0
    switch_cache = _MatrixRowSwitchCache(
        row_size=doe.shape[0], column_size=doe.shape[1]
    )
    old_switch_cache = _MatrixRowSwitchCache(
        row_size=doe.shape[0], column_size=doe.shape[1]
    )
    for i_try in range(2, steps + 1):
        if switch_cache.is_full:
            logging.info("No more perturbation left to improve the score")
            break
        doe_try = switch_cache.switch_rows_and_cache(doe_start.copy())
        curr_score = scorer(doe_try)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="overflow")
            transition_probability = np.exp(
                -(anneal_step_score - curr_score) / temperature
            )

        if (
            curr_score > anneal_step_score
            or np.random.random() <= transition_probability
        ):
            doe_start = doe_try.copy()
            old_switch_cache = deepcopy(switch_cache)
            anneal_step_score = curr_score
            switch_cache.reset()
            temperature = cool_down_temperature(temperature)
            if curr_score > best_score:
                best_doe = doe_try.copy()
                best_score = curr_score
                steps_without_improvement = 0
                logging.debug(
                    f"{i_try} - start score improved by {100 * abs((best_score - start_score) / start_score):.1f}%"
                )
        steps_without_improvement += 1

        if steps_without_improvement >= max_steps_without_improvement:
            temperature = cool_down_temperature(temperature)
            # Bound Randomness by setting back to best result
            # This often accelerates convergence speed
            doe_start = best_doe.copy()
            switch_cache = deepcopy(old_switch_cache)
            anneal_step_score = best_score
            steps_without_improvement = 0

    logging.info(
        f"Final score improved start score by {100 * abs((best_score - start_score) / start_score):.1f}% in {steps} steps"
    )
    return best_doe


@dataclass
class _MatrixRowSwitchCache:
    """A cache that is used in simulated annealing to avoid repeating the same perturbations"""

    row_size: int
    column_size: int
    _max_switches_per_column: int = field(init=False, repr=False, default=None)
    _cache: list[np.ndarray] = field(init=False, repr=False, default=None)
    _cache_sizes: np.ndarray = field(init=False, repr=False, default=None)

    def __post_init__(self) -> None:
        # We switch two rows, thus the magic number
        self._max_switches_per_column = combine(self.row_size, 2)
        self.reset()

    @property
    def is_full(self) -> bool:
        return np.min(self._cache_sizes) >= self._max_switches_per_column

    def reset(self) -> None:
        self._cache_sizes = np.zeros(self.column_size, dtype=int)
        self._cache = [np.zeros((0, 2), dtype=int) for _ in range(self.column_size)]

    def choose_column(self) -> int:
        return np.random.choice(
            np.where(self._cache_sizes < self._max_switches_per_column)[0]
        )

    def choose_rows(self, column: int) -> tuple[int, int]:
        def choose_non_occupied(occupied: set[int]) -> int:
            return np.random.choice(
                [idx for idx in range(self.row_size) if idx not in occupied]
            )

        row_cache = self._cache[column]
        max_switches_per_row = self.row_size - 1
        fulls, counts = np.unique(row_cache, return_counts=True)
        row_1 = choose_non_occupied(set(fulls[counts >= max_switches_per_row]))
        row_2 = choose_non_occupied(
            set(row_cache[np.any(row_cache == row_1, axis=1)].ravel())
        )
        return row_1, row_2

    def cache(self, column: int, row_1: int, row_2: int) -> None:
        self._cache[column] = np.append(
            self._cache[column], np.array([[row_1, row_2]]), axis=0
        )
        self._cache_sizes[column] += 1

    def switch_rows_and_cache(self, matrix: np.ndarray) -> np.ndarray:
        column = self.choose_column()
        row_1, row_2 = self.choose_rows(column)
        self.cache(column, row_1, row_2)
        matrix[row_1, column], matrix[row_2, column] = (
            matrix[row_2, column],
            matrix[row_1, column],
        )
        return matrix
