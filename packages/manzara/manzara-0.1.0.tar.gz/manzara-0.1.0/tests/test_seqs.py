from manzara.seqs import Seq, Space


def test_hamming_distance():
    assert Seq("ABCDE").hamming_distance(Seq("AACBE")) == 2


def test_seq_equality():
    assert Seq("000") != Seq((0, 0, 0))
    assert Seq("000") == Seq(("0", "0", "0"))
    assert Seq("000") is not Seq("000")


def test_space_size():
    space = Space(5, range(10))
    assert len(list(space.seqs)) == len(space) == 10**5


def test_space_seqs():
    space = Space(2, ("0", "1", "2"))
    assert set(space.seqs) == {
        Seq("00"),
        Seq("01"),
        Seq("02"),
        Seq("10"),
        Seq("11"),
        Seq("12"),
        Seq("20"),
        Seq("21"),
        Seq("22"),
    }


def test_seq_border():
    space = Space(2)
    seq = Seq("00")
    assert set(space.border(seq, 2)) == {Seq("11")}
    assert set(space.border(seq, 1)) == {Seq("01"), Seq("10")}


def test_seq_neighborhood():
    space = Space(2)
    seq = Seq("00")
    assert set(space.neighborhood(Seq("00"), 2)) == set(space.seqs).difference([seq])


def test_random_seq_completeness():
    space = Space(4)
    assert len(set([space.random_seq() for _ in range(10**4)])) == len(space)
