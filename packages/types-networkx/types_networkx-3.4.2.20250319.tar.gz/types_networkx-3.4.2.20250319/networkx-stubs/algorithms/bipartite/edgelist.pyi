from _typeshed import Incomplete
from collections.abc import Generator

from networkx.classes.graph import Graph, _Node
from networkx.utils.backends import _dispatchable

@_dispatchable
def write_edgelist(G, path, comments: str = "#", delimiter: str = " ", data: bool = True, encoding: str = "utf-8") -> None: ...
@_dispatchable
def generate_edgelist(G, delimiter: str = " ", data: bool = True) -> Generator[Incomplete, None, None]: ...
@_dispatchable
def parse_edgelist(
    lines,
    comments: str | None = "#",
    delimiter: str | None = None,
    create_using: Graph[_Node] | None = None,
    nodetype=None,
    data=True,
): ...
@_dispatchable
def read_edgelist(
    path,
    comments: str | None = "#",
    delimiter: str | None = None,
    create_using=None,
    nodetype=None,
    data=True,
    edgetype=None,
    encoding: str | None = "utf-8",
): ...
