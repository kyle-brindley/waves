import pathlib
from unittest.mock import patch

import pytest
import networkx
import matplotlib.pyplot

from waves import _visualize


def test_ancestor_subgraph():
    graph = networkx.DiGraph()
    graph.add_edge("parent", "child")

    # Check for a runtime error on empty subgraph/missing node
    with pytest.raises(RuntimeError):
        subgraph = _visualize.ancestor_subgraph(graph, ["notanode"])

    # Check subgraph(s)
    subgraph = _visualize.ancestor_subgraph(graph, ["child"])
    assert subgraph.nodes == graph.nodes

    # Check subgraph(s)
    subgraph = _visualize.ancestor_subgraph(graph, ["parent"])
    assert list(subgraph.nodes) == ["parent"]


def test_add_node_count():
    graph = networkx.DiGraph()
    graph.add_node(1, label="one", layer=1)
    graph.add_node(2, label="two", layer=2)
    graph.add_edge(1, 2)
    new_graph = _visualize.add_node_count(graph)
    assert "Node count: 2" in new_graph.nodes


def test_graph_to_graphml():
    """Sign-of-life test for a non-empty Python string return value.

    Testing the content of an XML file subject to change with data unrelated to the input is fragile. If something more
    than a sign-of-life test is performed, it should probably include converting the XML back into a graph object and
    testing equality of the graph objects.
    """
    graph = networkx.DiGraph()
    graph.add_edge(1, 2)
    graphml = _visualize.graph_to_graphml(graph)
    assert isinstance(graphml, str)
    assert graphml != ""


def test_parse_output():
    """Test raises behavior and regression test a sample SCons tree output parsing"""
    # Check for a runtime error on empty parsing
    with pytest.raises(RuntimeError):
        graph = _visualize.parse_output([])

    # Sign-of-life with partial reproduction of modsim template nominal tree output
    tree_output = "[E b   C  ]+-nominal\n[  B      ]  +-build/nominal/stress_strain_comparison.pdf"
    tree_lines = tree_output.split("\n")
    graph = _visualize.parse_output(tree_lines)
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert "nominal" in graph.nodes
    assert "build/nominal/stress_strain_comparison.pdf" in graph.nodes


def test_check_regex_exclude():
    """Test the regular expression exclusion of the visualize subcommand"""
    exclude_regex = "dummy_name[0-7]+"
    # If node name matches the regular expression
    assert _visualize.check_regex_exclude(exclude_regex, "dummy_name5", 3, 0, False) == (True, 3)
    # if node name does not match the regular expression
    assert _visualize.check_regex_exclude(exclude_regex, "dummy_name8", 2, 1, False) == (False, 1)
    # If node name does not match the regular expression but the node was already excluded
    assert _visualize.check_regex_exclude(exclude_regex, "dummy_name9", 4, 2, True) == (True, 2)


def test_visualize():
    """Sign-of-life test for the visualize figure"""
    graph = networkx.DiGraph()
    graph.add_node(1, label="one", layer=1)
    graph.add_node(2, label="two", layer=2)
    graph.add_edge(1, 2)
    _visualize.visualize(graph)


def test_plot():
    """Check that the expected plot output function is called"""
    figure, axes = matplotlib.pyplot.subplots()
    with (
        patch("matplotlib.pyplot.show") as mock_show,
        patch("matplotlib.figure.Figure.savefig") as mock_savefig,
    ):
        _visualize.plot(figure, output_file=None)
    mock_show.assert_called_once()
    mock_savefig.assert_not_called()

    with (
        patch("matplotlib.pyplot.show") as mock_show,
        patch("matplotlib.figure.Figure.savefig") as mock_savefig,
    ):
        _visualize.plot(figure, output_file=pathlib.Path("dummy.png"))
    mock_savefig.assert_called_once()
    mock_show.assert_not_called()
