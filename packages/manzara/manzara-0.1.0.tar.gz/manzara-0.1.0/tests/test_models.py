import pytest

from manzara import landscapes
from manzara.seqs import Seq, Space


@pytest.fixture
def spaces():
    return {
        "small": Space(3),
        "medium": Space(5, tuple(range(5))),
        "big": Space(10, tuple(range(20))),
    }


def test_house_of_cards_model(spaces):
    model = landscapes.HouseOfCards(space=spaces["medium"])
    assert len(set(model.fitness(seq) for seq in model.space)) == len(model.space)


@pytest.mark.parametrize("k", range(5))
def test_flat_nk_model(spaces, k):
    space = spaces["medium"]
    model = landscapes.NK(space=space, contribution_draw=(lambda: 0), k=k)
    assert model.n_local_maxima() == 0
    for locus in space.loci:
        assert len(model.partners[locus]) == len(set(model.partners[locus])) == k + 1


def test_smooth_nk_model(spaces):
    model = landscapes.NK(space=spaces["medium"], k=0)
    seq1 = Seq([0] * 5)
    seq2 = seq1.substitute([0], [3])
    contribution_diff = model.contribution(seq2, 0) - model.contribution(seq1, 0)
    assert contribution_diff
    assert model.fitness(seq2) - model.fitness(seq1) == pytest.approx(contribution_diff)


def test_rough_nk_model(spaces):
    space = spaces["medium"]
    model = landscapes.NK(space=space, k=space.seq_len - 1)
    seq1 = Seq([space.alphabet[0]] * space.seq_len)
    seq1_contributions = [model.contribution(seq1, locus) for locus in space.loci]
    seq2 = seq1.substitute([0], [space.alphabet[1]])
    seq2_contributions = [model.contribution(seq2, locus) for locus in space.loci]
    assert not set(seq1_contributions).intersection(seq2_contributions)


@pytest.mark.parametrize("c", [0.01, 1, 10])
def test_rough_mt_fuji_model(spaces, c):
    model = landscapes.RoughMtFuji(space=spaces["medium"], c=c, noise_draw=None)
    assert model.global_max() == model.reference_seq
    assert model.n_local_maxima() == 1


def test_linear_model(spaces):
    model = landscapes.Linear(space=spaces["small"])
    f1 = model.fitness(Seq("000"))
    f2 = model.fitness(Seq("001"))
    c1 = model.coefficient(((2, "0"),))
    c2 = model.coefficient(((2, "1"),))
    assert f2 - f1 == pytest.approx(c2 - c1)


@pytest.mark.parametrize("d", [1, 10, 100])
def test_stickbreaking_model(spaces, d):
    model = landscapes.Stickbreaking(space=spaces["big"], d=d)
    seqs = [next(model.space.seqs) for _ in range(10**3)]
    assert all(0 < model.fitness(seq) < d for seq in seqs)
