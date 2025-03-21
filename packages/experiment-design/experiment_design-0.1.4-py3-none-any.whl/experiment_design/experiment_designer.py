import abc

import numpy as np

from experiment_design.scorers import (
    Scorer,
    ScorerFactory,
    create_default_scorer_factory,
)
from experiment_design.variable import ParameterSpace

DEFAULT_INITIAL_OPTIMIZATION_PROPORTION = 0.1


class ExperimentDesigner(abc.ABC):
    """
    Abstract class of experiment designers that create and extend designs of experiments, i.e. experiment plans

    :param scorer_factory: A factory that creates scorers for the given variables, sample_size and in the cast of an
        extension, old sampling points. If not passed, a default one will be created, that evaluates the maximum
        correlation error and minimum pairwise distance. See `experiment_design.scorers.create_default_scorer_factory`
        for more details.
    """

    def __init__(self, scorer_factory: ScorerFactory | None = None) -> None:
        if scorer_factory is None:
            scorer_factory = create_default_scorer_factory()
        self.scorer_factory = scorer_factory

    def design(
        self,
        space: ParameterSpace,
        sample_size: int,
        old_sample: np.ndarray | None = None,
        steps: int | None = None,
        initial_optimization_proportion: float = DEFAULT_INITIAL_OPTIMIZATION_PROPORTION,
    ) -> np.ndarray:
        """
        Create or extend a |DoE| .

        :param space: Determines the dimensions of the resulting sample.
        :param sample_size: The number of points to be created.
        :param old_sample: Old |DoE| matrix with shape (old_sample_size, space.dimensions). If provided,
            it will be extended with sample_size new points, otherwise a new |DoE| will be created.
            In both cases, only the new points will be returned.
        :param steps: Number of search steps for improving the |DoE| quality wrt. the self.scorer_factory.
        :param initial_optimization_proportion:  Proportion of steps that will be used to create an
            initial |DoE| with a good score. Rest of the steps will be used to optimize the candidate points.
        :return: |DoE| matrix with shape (sample_size, space.dimensions)
        """
        scorer = self.scorer_factory(space, sample_size, old_sample=old_sample)
        initial_steps, final_steps = calculate_optimization_step_numbers(
            sample_size, steps, proportion=initial_optimization_proportion
        )
        if old_sample is None:
            return self._create(space, sample_size, scorer, initial_steps, final_steps)
        return self._extend(
            old_sample,
            space,
            sample_size,
            scorer,
            initial_steps,
            final_steps,
        )

    @abc.abstractmethod
    def _create(
        self,
        space: ParameterSpace,
        sample_size: int,
        scorer: Scorer,
        initial_steps: int,
        final_steps: int,
    ) -> np.ndarray:
        raise NotImplementedError

    @abc.abstractmethod
    def _extend(
        self,
        old_sample: np.ndarray,
        space: ParameterSpace,
        sample_size: int,
        scorer: Scorer,
        initial_steps: int,
        final_steps: int,
    ) -> np.ndarray:
        raise NotImplementedError


def calculate_optimization_step_numbers(
    sample_size: int,
    steps: int | None = None,
    proportion: float = DEFAULT_INITIAL_OPTIMIZATION_PROPORTION,
) -> tuple[int, int]:
    """
    Calculate the proportion of steps to be used for the initial and final optimizations.
    Also provide a sensible default total number of steps if they are not provided

    :param sample_size: The number of samples to be created. Only used to guess steps if it is
        not provided.
    :param steps: The number of total steps. If not passed, it will be guessed depending on the
        sample_size.
    :param proportion: Proportion of initial to total steps.
    :return: initial and final optimization steps (minimum 1 for each stage).

    :meta private:
    """
    if steps is None:
        if sample_size <= 128:
            steps = 20_000
        else:
            steps = 2_000
    init_steps = max(1, round(proportion * steps))
    opt_steps = max(0, steps - init_steps)
    return init_steps, opt_steps
