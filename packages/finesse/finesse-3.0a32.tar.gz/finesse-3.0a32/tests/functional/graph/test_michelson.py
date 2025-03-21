from finesse.simulations.graph.tools import ModelOperatorPicture
import finesse
import pytest


@pytest.fixture()
def michelson():
    return finesse.script.parse(
        """
                             l l1
                             bs bs
                             m itmx
                             m itmy
                             link(l1, 1, bs.p1)
                             link(bs.p2, 1, itmy)
                             link(bs.p3, 1, itmx)
                             """
    )


@pytest.fixture()
def michelson_op(michelson):
    return ModelOperatorPicture(michelson)


def test_all_source_and_sinks(michelson_op):
    # No nodes with inputs and outputs
    assert len(michelson_op.graph.evaluation_nodes()) == 0


def test_input_to_AS(michelson_op):
    # Should be a sum of the two arms
    solution = (
        "+",
        (
            "*",
            "l1_p1__bs_p1.P1i_P2o",
            "bs.P1i_P3o",
            "bs_p3__itmx_p1.P1i_P2o",
            "itmx.P1i_P1o",
            ("*", "bs_p3__itmx_p1.P2i_P1o", "bs.P3i_P4o"),
        ),
        (
            "*",
            "l1_p1__bs_p1.P1i_P2o",
            "bs.P1i_P2o",
            "bs_p2__itmy_p1.P1i_P2o",
            "itmy.P1i_P1o",
            ("*", "bs_p2__itmy_p1.P2i_P1o", "bs.P2i_P4o"),
        ),
    )

    assert michelson_op.graph.get_edge_operator_expression(1, 9) == solution
