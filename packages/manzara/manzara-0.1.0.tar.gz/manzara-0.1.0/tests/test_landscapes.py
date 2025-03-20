import pytest
import random

from manzara import landscapes
from manzara.seqs import Seq, Space


def spaces():
    return (Space(3),)


def models():
    models = []
    for space in spaces():
        models.extend(
            [
                landscapes.HouseOfCards(space=space),
                landscapes.NK(space=space, k=2),
                landscapes.RoughMtFuji(
                    space=space, c=0.1, noise_draw=lambda: random.expovariate(10)
                ),
                landscapes.Stickbreaking(space=space, d=2),
                landscapes.Linear(
                    space=space, coefficient_draw=tuple([random.expovariate] * 2)
                ),
            ]
        )
    return models


@pytest.mark.parametrize("model", models())
def test_consistency(model):
    f1 = model.fitness(Seq("110"))
    model.fitness(Seq("001"))
    f1_again = model.fitness(Seq("110"))
    assert f1 == f1_again


def test_consistency_of_walk():
    space = Space(15)
    model = landscapes.NK(space=space, k=5)

    final_distances = []
    for _ in range(3):
        space = Space(15)
        seq = Seq("010" * 5)
        dfes = []
        for _ in range(5):
            dfes.append(model.dfe(seq, radius=2))
            seq = max(
                space.neighborhood(seq, radius=2), key=lambda seq: model.fitness(seq)
            )
        final_distances.append(seq.hamming_distance(model.global_max()))

    assert all(d == final_distances[0] for d in final_distances)


@pytest.mark.parametrize("space", spaces())
def test_inconsistency_warned(recwarn, space):
    with pytest.warns(UserWarning, match="consistent"):
        landscapes.HouseOfCards(space=space, store=False)
    landscapes.HouseOfCards(space=space, store=False)
    assert recwarn


@pytest.mark.parametrize("space", spaces())
def test_consistency_not_warned(recwarn, space):
    landscapes.HouseOfCards(space=space, store=True)
    landscapes.Stickbreaking(space=space)
    assert not recwarn


@pytest.mark.parametrize("model", models())
def test_local_max(model):
    local_max = next(model.local_maxima())
    assert all(
        model.fitness(local_max) > model.fitness(seq)
        for seq in model.space.neighborhood(local_max)
    )


@pytest.mark.parametrize("model", models())
def test_global_max(model):
    max_seq = model.global_max()
    assert max(model.fitness(seq) for seq in model.space.seqs) == model.fitness(max_seq)
    assert model.local_max(max_seq)
    assert max_seq in model.local_maxima()


def test_allele_combinations():
    assert set(Seq("ABC").allele_combinations(2)) == set(
        [
            ((0, "A"), (1, "B")),
            ((0, "A"), (2, "C")),
            ((1, "B"), (2, "C")),
        ]
    )


@pytest.mark.parametrize("model", models())
def test_dfe(model):
    assert len(list(model.dfe(Seq("000"), radius=2))) == 3 + 3
    local_max = next(model.local_maxima())
    assert all(effect < 0 for effect in model.dfe(local_max))
