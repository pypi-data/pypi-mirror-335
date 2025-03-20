from pytest_funcnodes import all_nodes_tested
from funcnodes_opencv import NODE_SHELF


def test_all_nodes_tested(all_nodes):
    all_nodes_tested(
        all_nodes,
        NODE_SHELF,
    )
