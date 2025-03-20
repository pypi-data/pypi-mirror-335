import random
import operator
import warnings
from math import prod
from functools import cache, cached_property
from abc import ABC, abstractmethod
from typing import Optional, Callable, Iterator

from .seqs import Seq, Space


class FitnessLandscape(ABC):
    """
    Holds methods and properties common to landscape models. Also responsible
    for handling consistency and reproducibility. Some models are intrinsically
    consistent and don't need to cache fitnesses of particular fitnesses.
    """

    intrinsically_consistent = False

    def __init__(self, space: Space, store: bool = True):
        self.space = space
        self.store = False if self.intrinsically_consistent else store
        if not self.consistent:
            warnings.warn(
                "The landscape appears set to be inconsistent: it may not work as expected."
            )

    def __repr__(self):
        class_name = self.__class__.__name__
        kwarg_str = ", ".join(f"{k}={str(v)}" for k, v in vars(self).items())
        return f"{class_name}({kwarg_str})"

    @abstractmethod
    def _fitness(self, seq: Seq) -> float:
        pass

    @property
    def consistent(self) -> bool:
        return self.intrinsically_consistent or self.store

    @cache
    def _visited(self, seq: Seq) -> float:
        return self._fitness(seq)

    def fitness(self, seq: Seq) -> float:
        """
        Compute the fitness of the given seq, ensuring consistency if enabled.
        """
        assert set(seq).issubset(self.space.alphaset)
        assert len(seq) == self.space.seq_len
        if self.store:
            return self._visited(seq)
        return self._fitness(seq)

    def dfe(self, seq: Seq, radius: int = 1) -> Iterator[float]:
        """
        The distribution of fitness effects of all mutations within the given
        mutational distance.
        """
        for neighbor in self.space.neighborhood(seq, radius):
            yield self.fitness(neighbor) - self.fitness(seq)

    @cache
    def global_max(self, reverse: bool = False) -> Seq:
        """Returns the maximum-fitness sequence in the space."""
        compare = min if reverse else max
        return compare(self.space.seqs, key=lambda seq: self.fitness(seq))

    def local_max(self, seq: Seq, radius: int = 1, reverse: bool = False) -> bool:
        """
        Assesses whether a sequence is a local maximum within the given
        mutational distance. Setting reverse=True will assess whether it's
        a local minimum.
        """
        compare = operator.lt if reverse else operator.gt
        return all(
            compare(self.fitness(seq), self.fitness(neighbor))
            for neighbor in self.space.neighborhood(seq, radius)
        )

    def local_maxima(self, **local_max_kwargs) -> Iterator[Seq]:
        yield from (
            seq for seq in self.space.seqs if self.local_max(seq, **local_max_kwargs)
        )

    def n_local_maxima(self, **local_max_kwargs) -> int:
        return sum(1 for _ in self.local_maxima(**local_max_kwargs))


def intrinsically_consistent(cls):
    """Some models don't require external enforcement of consistency."""
    cls.intrinsically_consistent = True
    return cls


class HouseOfCards(FitnessLandscape):
    """
    This model returns a fitness, randomly drawn from a given distribution
    (fitness_draw), for each new sequence.
    """

    def __init__(self, fitness_draw: Callable = random.expovariate, **landscape_kwargs):
        super().__init__(**landscape_kwargs)
        self.fitness_draw = fitness_draw

    def _fitness(self, seq: Seq) -> float:
        return self.fitness_draw()


@intrinsically_consistent
class NK(FitnessLandscape):
    """
    Based on Kauffman and Weinberger's 1989 description. Each locus interacts
    with k other loci and itself. Each time a new combination of these
    interacting loci is seen, a new fitness contribution of the locus is drawn
    according to a given distribution (contribution_draw). The fitness of the
    sequence is the sum of the locus contributions.
    """

    def __init__(
        self,
        k: int = 0,
        contribution_draw: Callable = random.expovariate,
        **landscape_kwargs,
    ):
        super().__init__(**landscape_kwargs)
        self.k = k
        self.contribution_draw = contribution_draw

    @property
    def n(self) -> int:
        return self.space.seq_len

    @cached_property
    def partners(self) -> dict[int, list[int]]:
        loci = self.space.loci
        return {
            locus: ([locus] + random.sample(loci[:locus] + loci[locus + 1 :], self.k))
            for locus in loci
        }

    @cache
    def _contribution_draw(self, locus: int, state: tuple) -> float:
        return self.contribution_draw()

    def contribution(self, seq: Seq, locus: int):
        state = tuple(seq.at(self.partners[locus]))
        return self._contribution_draw(locus, state)

    def _fitness(self, seq: Seq) -> float:
        return sum(self.contribution(seq, locus) for locus in self.space.loci)


class RoughMtFuji(FitnessLandscape):
    """
    Based on the version by Neidhart et al. in Genetics (2014). Fitnesses
    decrease with mutational distance from a reference sequence according
    to the rate c > 0, with sequence-wise noise contributed by noise_draw.
    The reference sequence is set randomly if none is provided.
    """

    def __init__(
        self,
        c: float = 1,
        noise_draw: Optional[Callable] = random.expovariate,
        reference_seq: Optional[Seq] = None,
        **landscape_kwargs,
    ):
        super().__init__(**landscape_kwargs)
        self.c = c
        self.noise_draw = (lambda: 0) if noise_draw is None else noise_draw
        self.reference_seq = (
            self.space.random_seq() if reference_seq is None else reference_seq
        )

    def _fitness(self, seq: Seq) -> float:
        return -self.c * seq.hamming_distance(self.reference_seq) + self.noise_draw()


@intrinsically_consistent
class Linear(FitnessLandscape):
    """
    Combinations of mutations are assumed to have an effect specified at
    each order of interaction by coefficient_draw. These effects add up.
    The maximum order of epistatic interaction is set by the length of
    coefficient_draw, such that coefficient_draw=(random.expovariate,),
    for example, represents no epistasis and that single-locus alleles
    have Exponential(1)-distributed effects.
    """

    def __init__(
        self,
        coefficient_draw: tuple[Callable, ...] = (random.expovariate,),
        **landscape_kwargs,
    ):
        super().__init__(**landscape_kwargs)
        self.coefficient_draw = coefficient_draw

    @cached_property
    def epistasis_orders(self) -> tuple[int, ...]:
        return tuple(range(1, len(self.coefficient_draw) + 1))

    @cache
    def coefficient(self, combination: tuple) -> float:
        order = len(combination)
        return self.coefficient_draw[order - 1]()

    def _fitness(self, seq: Seq) -> float:
        return sum(
            self.coefficient(combination)
            for order in self.epistasis_orders
            for combination in seq.allele_combinations(order)
        )


@intrinsically_consistent
class Stickbreaking(FitnessLandscape):
    """
    Based on Nagel et al. in Genetics (2012). The effects of single-locus
    alleles (distributed according to weight_draw) combine gradually toward
    a fitness limit, d.
    """

    def __init__(
        self,
        d: float = 1,
        weight_draw: Callable = lambda: random.betavariate(1, 1),
        **landscape_kwargs,
    ):
        super().__init__(**landscape_kwargs)
        self.d = d
        self.weight_draw = weight_draw

    @cache
    def weight(self, locus: int, allele) -> float:
        return self.weight_draw()

    def _fitness(self, seq: Seq) -> float:
        return self.d * (
            1 - prod(1 - self.weight(locus, allele) for locus, allele in enumerate(seq))
        )
