import random
import itertools
from collections.abc import Sequence
from functools import cached_property
from typing import Self, Iterable, Iterator, Hashable


class Seq(Sequence):
    "A sequence, internally represented as a tuple."

    def __init__(self, seq: Iterable[Hashable]):
        self.seq = tuple(seq)
        assert isinstance(self.seq, Hashable)

    def __getitem__(self, locus):
        return self.seq[locus]

    def __len__(self):
        return len(self.seq)

    def __repr__(self):
        return f"Seq({self.seq})"

    def __eq__(self, other):
        return self.seq == other.seq

    def __hash__(self):
        return hash(self.seq)

    @property
    def loci(self) -> tuple[int, ...]:
        return tuple(range(len(self)))

    def at(self, loci: Iterable[int]) -> list:
        """The alleles at each of the given loci, in order."""
        return [self[locus] for locus in loci]

    def allele_combinations(self, k: int = 1) -> Iterator[tuple[tuple, ...]]:
        """All the possible combinations of k of the sequence's alleles."""
        for locus_combination in itertools.combinations(self.loci, k):
            yield tuple((locus, self[locus]) for locus in locus_combination)

    def substitute(self, loci: Iterable[int], substitutions: Iterable) -> Self:
        """Create a sequence with the given substitutions corresponding to the given loci."""
        new_seq = list(self.seq)
        for locus, new in zip(loci, substitutions):
            new_seq[locus] = new
        return self.__class__(new_seq)

    def hamming_distance(self, other: Self) -> int:
        return sum(c1 != c2 for c1, c2 in zip(self, other))


class Space:
    """
    A sequence space, representing all sequences of a given length and alphabet.
    """

    def __init__(self, seq_len: int, alphabet: tuple = ("0", "1")):
        self.seq_len = seq_len
        self.alphabet = alphabet

    def __iter__(self):
        yield from self.seqs

    def __len__(self):
        return len(self.alphabet) ** self.seq_len

    def __repr__(self):
        return f"Space(seq_len={self.seq_len}, alphabet={self.alphabet})"

    @cached_property
    def loci(self) -> tuple[int, ...]:
        return tuple(range(self.seq_len))

    @cached_property
    def alphaset(self) -> set:
        return set(self.alphabet)

    @property
    def seqs(self) -> Iterator[Seq]:
        """All the sequences in the space."""
        for seq in itertools.product(self.alphabet, repeat=self.seq_len):
            yield Seq(seq)

    def border(self, seq: Seq, k: int = 1) -> Iterator[Seq]:
        """All the sequences exactly a k-mutation distance from the given sequence."""
        for loci in itertools.combinations(seq.loci, k):
            allele_choices = [self.alphaset.difference([seq[locus]]) for locus in loci]
            for substitutions in itertools.product(*allele_choices):
                yield seq.substitute(loci, substitutions)

    def neighborhood(self, seq: Seq, radius: int = 1) -> Iterator[Seq]:
        """
        All the sequences at most a k-mutation distance from the given sequence,
        excluding the sequence.
        """
        for d in range(1, radius + 1):
            yield from self.border(seq, d)

    def random_seq(self) -> Seq:
        return Seq(random.choices(self.alphabet, k=self.seq_len))
