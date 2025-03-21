"""Tests a simple cavity model with a tunable mirror and computing the operator picture
using a reduced graph."""

import finesse
import pytest

from finesse.simulations.graph.tools import ModelOperatorPicture


@pytest.fixture()
def model():
    model = finesse.script.parse(
        """
    l l1
    lens L1
    m m1
    m m2 T=0.1 R=0.9
    m m3 T=0.01 R=0.99
    link(l1, L1, m1, 200, m2, 2000, m3)
    """
    )
    return model


@pytest.fixture()
def op_pic(model):
    return ModelOperatorPicture(model.deepcopy())


@pytest.fixture()
def op_pic_misaligned(model):
    model = model.deepcopy()
    model.m3.misaligned = True
    return ModelOperatorPicture(model)


def test_self_loop(op_pic):
    assert op_pic.graph.self_loop_edges == ((11, 11), (15, 15))


def test_self_loop_misaligned(op_pic_misaligned):
    assert op_pic_misaligned.graph.self_loop_edges == ((11, 11),)
