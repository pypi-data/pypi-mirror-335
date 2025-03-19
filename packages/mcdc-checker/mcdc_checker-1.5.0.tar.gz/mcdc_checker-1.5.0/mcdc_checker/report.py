# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Contains report class for collecting and printing results
"""

import json
from hashlib import sha256


class Report:
    """Report class for collecting messages"""

    errors: dict[str, str] = {}
    """error message dictionary"""

    statistics: dict[str, str] = {}
    """statistic report dictionary"""

    errors_format_str = {
        "clang_parse_failed": "Clang failed to parse file",
        "failed_to_create_bdd": "No BDD could be created for decision",
        "invalid_operator_nesting": "Decision has invalid operator nesting",
        "unexpected_node": "Unexpected node was found in the AST",
        "bdd_is_not_tree_like": "BDD is not tree-like",
    }
    """error type set"""

    statistics_format_str = {
        "num_decisions": "Number of decisions: {}",
        "num_tree_like_decision": "Number of tree-like decisions: {}",
        "num_correctable_non_tree_like_decisions": "Number of correctable non-tree-like "
        "decisions: {}",
        "num_non_correctable_non_tree_like_decisions": "Number of non-correctable non-tree-like "
        "decisions: {}",
        "num_compiler_issues": "Number of compiler preprocess/parse errors: {}",
        "num_files_checked": "Number of files checked: {}",
    }
    """statistic format string set"""

    def __init__(self):
        self.reset_errors()
        self.reset_statistics()

    def reset_errors(self):
        """
        Initialize the global errors dictionary with no errors occurred, which is an empty
        list for each of the following error types:

        clang_parse_failed:
            Clang could not parse a given file. Make sure that the include paths
            are correct and complete.
        invalid_operator_nesting:
            A condition contains a decision operator. Please refactor the code in
            question.
        unexpected_node:
            While walking the AST a node could not be parsed. This is a bug in the
            MCDCTreeChecker.
        bdd_is_not_tree_like:
            A decision was found which has a non tree-like BDD. Refactor the code
            in question.

        Each of these lists should be appended with a tuple containing the
        location and a possible solution::

            ((filename, line, column), solution)
        """
        self.errors = {
            "clang_parse_failed": [],
            "failed_to_create_bdd": [],
            "invalid_operator_nesting": [],
            "unexpected_node": [],
            "bdd_is_not_tree_like": [],
        }

    def add_error(self, error_type, location, solution):
        """Adds an error to the error list, thread safe."""
        if error_type in self.errors:
            self.errors[error_type].append((location, solution))

    def increment_statistic(self, stat_type, value=1):
        """Increments a statistic, thread safe."""
        if stat_type in self.statistics:
            self.statistics[stat_type] += value

    def merge(self, other_report):
        """Merges another report into this one, thread-safe."""
        for error_type, error_list in other_report.errors.items():
            self.errors[error_type].extend(error_list)
        for stat_type, stat in other_report.statistics.items():
            self.statistics[stat_type] += stat

    def reset_statistics(self):
        """
        Initialize the global statistics dictionary.
        """
        self.statistics = {
            "num_decisions": 0,
            "num_tree_like_decision": 0,
            "num_correctable_non_tree_like_decisions": 0,
            "num_non_correctable_non_tree_like_decisions": 0,
            "num_compiler_issues": 0,
            "num_files_checked": 0,
        }

    def print_statistics(self):
        """
        Print statistics values
        """
        print(
            "\nStatistics (including decisions encountered multiple times, e.g. in included"
            " headers):"
        )
        for stat_type, stat in self.statistics.items():
            print("  " + self.statistics_format_str[stat_type].format(stat))

    def print_error_summary(self):
        """
        Print all errors which have been appended to the global error dictionary.
        """
        if any([len(error_list) > 0 for _, error_list in self.errors.items()]):
            print(
                "\nThe following errors were found (excluding decisions encountered multiple "
                "times, e.g. in headers):"
            )
        else:
            print("\nNo errors were found.")
        for error_type, error_list in self.errors.items():
            unique_errors = set(error_list)
            if len(unique_errors) > 0:
                print("  " + self.errors_format_str[error_type] + ":")
                for (filename, line, column), solution in unique_errors:
                    if line:
                        print(f"    file {filename} in line {line} column {column}")
                    else:
                        print(f"    file {filename}")

                    if solution:
                        print(f"      Found solution: {solution}")

    def save_json_report(self, file):
        """
        Store report as JSON format.
        """
        severity_map = {
            "clang_parse_failed": "blocker",
            "failed_to_create_bdd": "minor",
            "invalid_operator_nesting": "critical",
            "unexpected_node": "minor",
            "bdd_is_not_tree_like": "critical",
        }

        report = []

        for error_type, error_list in self.errors.items():
            unique_errors = set(error_list)
            if len(unique_errors) > 0:
                for (filename, line, column), solution in unique_errors:
                    digest = sha256()
                    digest.update(f"{file}{error_type}{solution}".encode("utf-8"))
                    fingerprint = digest.hexdigest()

                    report.append(
                        {
                            "type": "issue",
                            "description": f"{self.errors_format_str[error_type]}. "
                            f"Found solution: {solution}",
                            "check_name": error_type,
                            "categories": ["Bug Risk", "Complexity"],
                            "location": {
                                "path": filename,
                                "positions": {
                                    "begin": {"line": line, "column": column},
                                    "end": {"line": line, "column": column},
                                },
                            },
                            "severity": severity_map[error_type],
                            "fingerprint": fingerprint,
                        }
                    )

        with open(file, "w", encoding="utf-8") as _file:
            _file.write(json.dumps(report, indent=2))
