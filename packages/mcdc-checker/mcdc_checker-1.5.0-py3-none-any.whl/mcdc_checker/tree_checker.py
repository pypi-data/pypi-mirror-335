# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Contains MCDCTreeChecker with the algorithm to check for tree like structure
"""
import re
import sys
import os

import itertools

from mcdc_checker.helper import (
    is_interesting_decision,
    bdd_to_dot,
    check_bdd_is_tree,
    get_children_list,
)
from mcdc_checker.report import Report

import clang.cindex  # type: ignore[import-untyped]

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../PBL/include")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../PBDD/include")
import BDD  # type: ignore[import-untyped]


class MCDCTreeChecker:
    """
    The main class of this tool, which implements the logic to generate and walk
    the AST of a C file to find interesting decisions in the MCDC sense.

    Example:

    >>> report = Report()
    >>> c = MCDCTreeChecker("mcdc_checker/tests/test.h", report)
    >>> c.parse()
    >>> c.find_decision()
    >>> c.create_bdds()
    >>> c.check_bdds_are_tree_like()
      Non tree-like decision in file mcdc_checker/tests/test.h at line 8, column 9
    """

    def __init__(self, filename, report):
        """
        Creates a new MCDCTreeChecker to check the file referenced by *filename*.

        :param filename: The preprocessed source code file. This file is read,
            parsed and analyzed by the methods of this class.
        """
        self.filename = filename
        self.preprocessor_lines = open(self.filename, encoding="utf-8").readlines()
        self.debug = False
        self.exprs = []
        self.bdds = []
        self.literal_counter = 0
        self.tu = None
        self.report = report

    def parse(self):
        """
        Use libclang to parse the file referenced by self.filename. After
        calling this function, self.tu will contain the AST of the translation
        unit.
        """
        index = clang.cindex.Index.create()
        self.tu = index.parse(self.filename)

    def get_original_location(self, node):
        """
        Get the location (line, column) of *node* in the non-preprocessed
        original file by looking at the location markers inserted by clang into
        the preprocessed C code.

        This is used to print user-readable messages with line numbers
        referring to the original source file.
        """
        linemarker_offset = 1
        node_location_index = node.location.line - 1

        try:
            while not re.match(
                r'# \d+ ".*"',
                self.preprocessor_lines[node_location_index - linemarker_offset],
            ):
                linemarker_offset += 1
        except IndexError:
            # No preprocessor marker was found, either the code was not preprocessed
            # or the preprocessor didn't create linemarkers. Return the location of the
            # node.
            return self.filename, node.location.line, node.location.column

        linemarker = self.preprocessor_lines[node_location_index - linemarker_offset].split(" ")

        try:
            orig_line, orig_file = (
                int(linemarker[1]) + linemarker_offset - 1,
                linemarker[2].split('"')[1],
            )
        except ValueError:
            # Something went wrong when parsing the location comment
            return self.filename, node.location.line, node.location.column

        return orig_file, orig_line, node.location.column

    def check_no_more_interesting_operators_below(self, node, level):
        """
        Check that for no descendants of *node* the
        :class:`is_interesting_decision` function returns true. In case an
        offending node is found, an error message is printed and the global
        error dict is appended.

        This function is used to sanity check the C code so that a condition
        does not contain a decision.
        """
        if is_interesting_decision(node):
            print(
                "{}ERROR: Invalid operator nesting! {} [line={}, col={}]".format(
                    " " * (level * 2 + 2),
                    self.get_condition_spelling(node),
                    self.get_original_location(node)[1],
                    node.location.column,
                )
            )
            self.report.add_error(
                "invalid_operator_nesting", self.get_original_location(node), None
            )
        else:
            # Recursively call this function for each child of the given node
            if self.debug:
                print(
                    "{}Node {} [line={}, col={}]".format(
                        " " * (level * 2 + 2),
                        node.kind,
                        self.get_original_location(node)[1],
                        node.location.column,
                    )
                )
                for child in node.get_children():
                    self.check_no_more_interesting_operators_below(child, level + 1)
            else:
                for child in node.get_children():
                    self.check_no_more_interesting_operators_below(child, level)

    def get_condition_spelling(self, node):
        """
        Returns the name of a condition referenced by *node* in pseudo-C-like
        syntax. This function is used to name the found conditions in the BDD.

        The function supports the following C constructs:

            * Function calls
            * Conditional operators
            * Unary expressions (such as sizeof)
            * Member reference expressions (such as struct->member)
            * Binary Operators
            * Parens expressions
            * Array accesses
            * Compound Literals
            * Unions
            * Leaf nodes such as literals or declaration references

        For unexposed expressions it will try to generate the name for the
        descendants first. If that comes up empty, the name of the unexposed
        node itself will be used.
        """
        children = get_children_list(node)

        if len(children) == 0:
            # Handle leaf nodes by returning their spelling
            if node.kind in (
                clang.cindex.CursorKind.INTEGER_LITERAL,
                clang.cindex.CursorKind.FLOATING_LITERAL,
                clang.cindex.CursorKind.CHARACTER_LITERAL,
            ):
                return "".join(
                    [
                        token.spelling
                        for token in clang.cindex.TokenGroup.get_tokens(
                            node._tu, extent=node.extent
                        )
                    ]
                )
            if node.spelling:
                return node.spelling
            else:
                self.literal_counter += 1
                return f"literal_{self.literal_counter}"
        elif node.kind == clang.cindex.CursorKind.CALL_EXPR:
            # Handle function calls by concatenating the spelling of all
            # parameters (children) and the function's name (current node)
            params = ", ".join(self.get_condition_spelling(c) for c in children[1:])
            return node.spelling + f"({params})"
        elif node.kind == clang.cindex.CursorKind.CONDITIONAL_OPERATOR:
            return self.get_condition_spelling(children[0])
        elif node.kind == clang.cindex.CursorKind.CXX_UNARY_EXPR:
            # Handle unary expressions such as sizeof
            if len(children) > 0:
                return f"UnaryExpr({self.get_condition_spelling(children[0])})"
            else:
                self.literal_counter += 1
                return f"UnaryExpr(literal_{self.literal_counter})"
        elif node.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
            if len(children) > 0:
                # Handle member references such as struct->member
                return f"{self.get_condition_spelling(children[0])}->{node.spelling}"
            else:
                return node.spelling
        elif node.kind == clang.cindex.CursorKind.CSTYLE_CAST_EXPR:
            if len(children) == 1:
                return f"({self.get_condition_spelling(children[0])})"
            else:
                return "({}){}".format(
                    self.get_condition_spelling(children[0]),
                    self.get_condition_spelling(children[1]),
                )
        elif node.kind == clang.cindex.CursorKind.BINARY_OPERATOR and len(children) == 2:
            return "{} {} {}".format(
                self.get_condition_spelling(children[0]),
                node.spelling,
                self.get_condition_spelling(children[1]),
            )
        elif node.kind == clang.cindex.CursorKind.ARRAY_SUBSCRIPT_EXPR and len(children) == 2:
            return "{}[{}]".format(
                self.get_condition_spelling(children[0]),
                self.get_condition_spelling(children[1]),
            )
        elif node.kind == clang.cindex.CursorKind.COMPOUND_LITERAL_EXPR and len(children) == 2:
            return "CompoundLiteral({}, {})".format(
                self.get_condition_spelling(children[0]),
                self.get_condition_spelling(children[1]),
            )
        elif node.kind == clang.cindex.CursorKind.UNION_DECL and len(children) == 2:
            return "UnionDecl({}, {})".format(
                self.get_condition_spelling(children[0]),
                self.get_condition_spelling(children[1]),
            )
        elif len(children) == 1:
            # Handle nodes with a single children, such as parens expressions
            if node.kind == clang.cindex.CursorKind.PAREN_EXPR:
                return f"({self.get_condition_spelling(children[0])})"
            if node.kind == clang.cindex.CursorKind.UNEXPOSED_EXPR:
                from_children = self.get_condition_spelling(children[0])
                if from_children:
                    return from_children
                else:
                    return node.spelling
            else:
                if node.spelling:
                    return node.spelling
                else:
                    return self.get_condition_spelling(children[0])
        elif node.kind == clang.cindex.CursorKind.UNEXPOSED_EXPR or len(children) >= 2:
            # Handle unexposed expr nodes in a generic way
            return (
                "(" + ", ".join([self.get_condition_spelling(child) for child in children]) + ")"
            )
        else:
            # We encountered something which has more than two children
            print(
                "ERROR: Unexpected node or number of children: children={} kind={} line={}".format(
                    len(children), node.kind, self.get_original_location(node)[1]
                )
            )
            self.report.add_error("unexpected_node", self.get_original_location(node), None)

    def build_decision(self, node, level, expr, var_order):
        """
        Build a decision object which can be used in BDD object from a descision in the AST.

        :param node: The top level node of the decision in the AST
        :param level: Indentation level for debug messages
        :param expr: The expression is built recursively in this parameter.
            When first calling the method, this should be an empty dict.
        :param var_order: The variables discovered while building the expression.
            When first calling the method, this should be an empty list.

        After calling this functions, the *expr* and *var_order* values can be
        used in a BDD, which can be created with :class:`bdd_init`.
        """
        if is_interesting_decision(node):
            if self.debug:
                print(
                    "{}Decision {} [line={}, col={}]".format(
                        " " * (level * 2 + 2),
                        node.spelling,
                        self.get_original_location(node)[1],
                        node.location.column,
                    )
                )
            if node.binary_operator == clang.cindex.BinaryOperator.LAnd:
                expr["type"] = "and"
            elif node.binary_operator == clang.cindex.BinaryOperator.LOr:
                expr["type"] = "or"
            expr["expr1"] = {}
            expr["expr2"] = {}

            children = get_children_list(node)
            self.build_decision(children[0], level + 1, expr["expr1"], var_order)
            self.build_decision(children[1], level + 1, expr["expr2"], var_order)
        elif node.kind == clang.cindex.CursorKind.CONDITIONAL_OPERATOR:
            self.build_decision(get_children_list(node)[0], level, expr, var_order)
        elif node.kind == clang.cindex.CursorKind.PAREN_EXPR:
            for child in node.get_children():
                self.build_decision(child, level, expr, var_order)
        else:
            name = self.get_condition_spelling(node)
            expr["name"] = (name, 0)
            expr["type"] = "var"
            var_order.append(name)
            if self.debug:
                print(
                    "{}Node {} [line={}, col={}]".format(
                        " " * (level * 2 + 2),
                        node.kind,
                        self.get_original_location(node)[1],
                        node.location.column,
                    )
                )
            self.check_no_more_interesting_operators_below(node, level + 1)

    def find_decision(self, node=None, level=None):
        """
        Walk the AST recursively to find the top-level node of each decision.
        For each found node, the :class:`build_decision` method is called.

        :param node: The node to check if it is a decision. If this is None,
            the root of the AST will be used.
        :param level: Indentation level for debug messages. If None, zero will
            be used.
        """
        if not node:
            node = self.tu.cursor
        if not level:
            level = 0

        if is_interesting_decision(node):
            self.report.increment_statistic("num_decisions")

            expr = {}
            var_order = []

            self.build_decision(node, level, expr, var_order)
            self.exprs.append((expr, var_order, self.get_original_location(node)))
        else:
            if self.debug:
                print(
                    "{}Node {} [line={}, col={}]".format(
                        " " * (level * 2 + 2),
                        node.kind,
                        self.get_original_location(node)[1],
                        node.location.column,
                    )
                )
                for child in node.get_children():
                    self.find_decision(child, level + 1)
            else:
                for child in node.get_children():
                    self.find_decision(child, level)

    def bdd_init(self, expr, var_order):
        """
        Create a BDD dictionary from the given expression and variable ordering
        which can be used with the PBDD library.

        This is similar to the bdd_init function from PBDD itself, with the
        difference that it doesn't read an expression from a file but instead
        uses the expression passed in with parameter expr.

        :param expr: An expression as built by :class:`build_decision`.
        :param var_order: A variable order list as built by :class:`build_decision`.
        """
        num_vars = len(var_order)

        bdd = {
            "expr": expr,
            "t_table": {
                0: ((num_vars + 1), None, None),
                1: ((num_vars + 1), None, None),
            },
            "u": 1,
            "n": num_vars,
            "h_table": {},
            "var_order": var_order,
        }

        return bdd

    def create_bdds(self):
        """
        For each expression and variable order found in the source file, build
        a BDD with ITE (If-then-else) method.
        """
        for expr, var_order, location in self.exprs:
            try:
                bdd = self.bdd_init(expr, var_order)
                BDD.ite_build(bdd)
                self.bdds.append((bdd, location))
            except Exception:
                self.report.add_error("failed_to_create_bdd", location, None)

    def permutate_bdd_vars(self, bdd):
        """
        Permutate the variable order given in *bdd* in all possible ways, build
        a minimal BDD with the modified order and given expression and check if
        the resulting BDD is a tree.

        :param bdd: The BDD which shall be permutated. The expression is used unmodified.
        :returns: A tree-like BDD if one is found, None otherwise.
        """
        original_order = bdd["var_order"]
        expr = bdd["expr"]
        for order in itertools.permutations(original_order, len(original_order)):
            bdd = self.bdd_init(expr, list(order))
            BDD.reorder_ite_build(bdd)

            if check_bdd_is_tree(bdd):
                return bdd

    def check_bdds_are_tree_like(self):
        """
        For each BDD, check whether it is tree-like. If not try to find a
        tree-like solution by calling :class:`permutate_bdd_vars`. For each
        non-tree like BDD an error is appended to the global error dictionary
        together with the possible solution, if any.
        """
        for bdd, (orig_filename, line, column) in self.bdds:
            if not check_bdd_is_tree(bdd):
                print(
                    "  Non tree-like decision in file {} at line {}, column {}".format(
                        orig_filename, line, column
                    )
                )
                if bdd["n"] <= 5:
                    reordered_bdd = self.permutate_bdd_vars(bdd)
                    if reordered_bdd:
                        tree_order = reordered_bdd["var_order"]
                        bdd_to_dot(reordered_bdd, orig_filename, line, column, "reordered")
                    else:
                        tree_order = None
                else:
                    reordered_bdd = None
                    tree_order = None

                if tree_order:
                    self.report.increment_statistic("num_correctable_non_tree_like_decisions")
                else:
                    self.report.increment_statistic("num_non_correctable_non_tree_like_decisions")
                self.report.add_error(
                    "bdd_is_not_tree_like",
                    (orig_filename, line, column),
                    ", ".join(tree_order) if tree_order else None,
                )
                bdd_to_dot(bdd, orig_filename, line, column, "orig")
            else:
                self.report.increment_statistic("num_tree_like_decision")
                if self.debug:
                    print(
                        "  Decision in file {} in line {}, column {} is tree-like".format(
                            orig_filename, line, column
                        )
                    )
