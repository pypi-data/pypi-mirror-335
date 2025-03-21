"""Tests a simple cavity model with a tunable mirror and computing the operator picture
using a reduced graph."""

import finesse
import pytest
import numpy as np

from finesse.symbols import Variable
from finesse.simulations.graph.tools import ModelOperatorPicture


@pytest.fixture()
def model():
    model = finesse.script.parse(
        """
    l l1
    lens L1
    m m1
    m m2 T=0.1 R=0.9
    link(l1, L1, m1, 200, m2)
    pd P l1.p1.i
    pd Q m2.p1.o
    """
    )
    # Need to use old school phase relationship as the symbolics doesn't use
    # that yet
    model._settings.phase_config.v2_transmission_phase = True
    model.m2.phi.is_tunable = True
    return model


@pytest.fixture()
def model_op_pic(model):
    return ModelOperatorPicture(model)


def test_changing_symbols(model_op_pic):
    assert model_op_pic.changing_symbols == (model_op_pic.model.m2.phi.ref,)


def test_non_numeric_symbols(model_op_pic):
    assert model_op_pic.non_numeric_symbols == (
        Variable("_f_"),
        model_op_pic.model.m2.phi.ref,
    )


def test_self_loop(model_op_pic):
    assert model_op_pic.graph.self_loop_edges == ((11, 11),)


def test_graph(model_op_pic):
    assert model_op_pic.graph.number_of_nodes == 14
    assert model_op_pic.graph.in_degree(model_op_pic.node_index["l1.p1.o"]) == 0
    assert model_op_pic.graph.in_degree(model_op_pic.node_index["m2.p2.i"]) == 0
    # does not count self loop
    assert model_op_pic.graph.in_degree(model_op_pic.node_index["m1.p1.o"]) == 2
    assert model_op_pic.graph.source_nodes() == (
        model_op_pic.node_index["l1.p1.o"],
        model_op_pic.node_index["m2.p2.i"],
    )
    assert model_op_pic.graph.evaluation_nodes() == (
        model_op_pic.node_index["m2.p1.o"],
    )


def test_sparse_solver_comparison(model_op_pic):
    op = model_op_pic
    model = model_op_pic.model

    l1_p1_o = op.node_index["l1.p1.o"]
    l1_p1_i = op.node_index["l1.p1.i"]
    m2_p1_o = op.node_index["m2.p1.o"]
    E_l1_p1_o = Variable(f"E_{{{l1_p1_o}}}")

    sources = [l1_p1_o]
    subs = {
        Variable("_f_"): 0,
    }

    IN_2_REFL = op.solve(l1_p1_i, sources)
    IN_2_REFL = IN_2_REFL.substitute(subs).collect()
    f_IN_2_REFL = IN_2_REFL.lambdify(E_l1_p1_o, model.m2.phi.ref)

    IN_2_CIRC = op.solve(m2_p1_o, sources)
    IN_2_CIRC = IN_2_CIRC.substitute(subs).collect()
    f_IN_2_CIRC = IN_2_CIRC.lambdify(E_l1_p1_o, model.m2.phi.ref)

    sol = model.run("xaxis(m2.phi, lin, -90, +90, 100)")
    model.m2.phi.is_tunable = True  # stop it resetting
    phi = sol.x1
    assert np.allclose(abs(f_IN_2_REFL(np.sqrt(model.l1.P), phi)) ** 2, sol["P"])
    assert np.allclose(abs(f_IN_2_CIRC(np.sqrt(model.l1.P), phi)) ** 2, sol["Q"])
