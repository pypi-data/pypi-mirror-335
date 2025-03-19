# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Provides helper functions for tree_checker module
"""

import sys
import os

import clang.cindex  # type: ignore[import-untyped]

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../PBL/include")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../PBDD/include")
import BDD  # type: ignore[import-untyped]


def is_interesting_decision(node):
    """
    Returns true, if the given *node* is a binary operator at the top level of
    a interesting decision in the sense of MCDC. Otherwise false is returned.
    """
    try:
        return node.kind == clang.cindex.CursorKind.BINARY_OPERATOR and (
            node.binary_operator == clang.cindex.BinaryOperator.LAnd
            or node.binary_operator == clang.cindex.BinaryOperator.LOr
        )
    except AttributeError:
        print(
            "It looks like the version of Clang you have installed is too old.\n"
            "Please install Clang 19 or newer."
        )
        sys.exit(1)


def check_bdd_is_tree(bdd):
    """
    Returns true if the given *bdd* is a tree. Otherwise false is returned.

    In the context of this function, a BDD is a tree when every non-leaf node
    can be reached from the root via exactly one path. This is done by
    examining every edge in the T table of the BDD and saving the end node in a
    visitation list. If, at the end, the visitation list contains every node
    exactly once, the BDD is a tree.
    """
    visited = []
    for _, (_, l, h) in bdd["t_table"].items():
        if l and l != 0 and l != 1:
            visited.append(l)
        if h and h != 0 and h != 1:
            visited.append(h)

    return len(visited) == len(set(visited))


def bdd_to_dot(bdd, filename, line, column, suffix):
    """
    Save the dot graph of the *bdd* to a file. The parameters *filename*,
    *line*, *column* and *suffix* (in that order) are used to generate the
    filename of the resulting file.

    The *filename* parameter refers to the source file the graph is generated
    for. It may contain slashes which will be replaced by hyphens.

    The *line* and *column* refer to the top level binary operator of the decision
    represented by the BDD.

    An additional *suffix* can be appended to the filename of the resulting dot
    file to distinguish different graphs for the same decision.
    """
    BDD.dot_bdd(
        bdd,
        "file_{}_line_{}_col_{}_{}.dot".format(
            filename.replace(os.path.sep, "-"), line, column, suffix
        ),
    )


def get_children_list(node):
    """
    Get a list of children of the given *node*.

    Returns a true list instead of an iterable as node.get_children does. This
    means you can count the number of children with len() or access the n-th
    children with [n].
    """
    return [child for child in node.get_children()]
