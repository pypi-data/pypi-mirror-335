import operator

import h5py
import pytest

import h5xxhsum

splitter = operator.methodcaller("split", "/")


def _add_dset(grp, name):
    dset = grp.create_dataset(name, (10,))
    assert dset.name.startswith("/")
    return dset.name[1:]


@pytest.fixture
def h5file(tmp_path):
    fname = tmp_path / "a.hdf5"
    names = []
    with h5py.File(fname, "w-", track_order=True) as h5:
        names += [_add_dset(h5, "b")]

        grp = h5.create_group("B", track_order=True)
        names += [_add_dset(grp, "b")]
        names += [_add_dset(grp, "a")]

        grp = h5.create_group("z", track_order=True)
        names += [_add_dset(grp, "b")]
        names += [_add_dset(grp, "a")]

        names += [_add_dset(h5, "a")]
        names += [_add_dset(h5, "z-")]

        # check that insertion tracking is honored
        assert list(h5) == ["b", "B", "z", "a", "z-"]
        assert list(h5["B"]) == ["b", "a"]
        assert list(h5["z"]) == ["b", "a"]

    # check that example file is not trivially sorted
    assert names != sorted(names)

    return fname, names


def test_lexicographic(h5file):
    """check that File.visititems iterates in lexicographic order"""
    pth, names = h5file

    w = h5xxhsum.Walker()
    with h5py.File(pth, "r") as h5:
        h5.visititems(w)
    assert w.names == sorted(names, key=splitter)
