#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Main class for argument parsing arguments and exit codes.
"""

import argparse
import os
import sys
import tempfile
import concurrent.futures

from glob import glob
from typing import Sequence
from enum import Enum

from mcdc_checker.tree_checker import MCDCTreeChecker
from mcdc_checker.report import Report


class McdcExit(Enum):
    """Pre-defined exit codes"""

    NO_ERROR = 0
    ERROR_GENERIC = 1
    ERROR_FILES = 2
    INVALID_ARG = 3


def check_file(filename, include_paths, defines, options, debug) -> Report:
    """
    Check a file for non-tree like BDDs by preprocessing the file and using an
    MCDCTreeChecker instance.

    :param filename: Path to the file to check
    :param include_paths: List of include paths to pass to the preprocessor
    :param defines: List of defines to pass to the preprocessor
    :param debug: If set to true, debug messages will be printed while processing the file
    :param report: Report class for the output
    """
    report = Report()
    print(f"Processing file {filename}")

    # Call Clang preprocess and save to a temporary file
    tf = tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1])
    command = "clang {} {} {} -E {} > {}".format(
        " ".join("-I {}".format(x) for x in include_paths) if include_paths else "",
        " ".join("-D {}".format(x) for x in defines) if defines else "",
        " ".join("{}".format(x) for x in options) if options else "",
        filename,
        tf.name,
    )
    exitcode = os.system(command)

    if exitcode != 0:
        print(f"ERROR: Clang failed to preprocess the file {filename}")
        report.add_error("clang_parse_failed", (filename, None, None), None)
        report.increment_statistic("num_compiler_issues")
    if exitcode == 2:
        sys.exit(2)

    c = MCDCTreeChecker(tf.name, report)
    c.debug = debug
    c.parse()
    c.find_decision()
    c.create_bdds()
    c.check_bdds_are_tree_like()

    report.increment_statistic("num_files_checked")

    return report


def _parse_args(args: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(description="MCDC Tree Checker")
    parser.add_argument(
        "-j",
        "--json-output",
        action="store",
        type=str,
        metavar="file",
        help="Output JSON report to file",
    )
    parser.add_argument(
        "-I",
        "--include",
        action="append",
        type=str,
        nargs="+",
        help="Add include path for preprocessor",
    )
    parser.add_argument(
        "-D",
        "--define",
        action="append",
        type=str,
        nargs="+",
        help="Add define for preprocessor",
    )
    parser.add_argument(
        "-O",
        "--options",
        action="append",
        type=str,
        nargs="+",
        help="Add extra flags to preprocessor calls",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        required=False,
        help="Check all C/C++ implementation and header files in current directory recursively",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        required=False,
        help="Enable additional debug output",
    )
    parser.add_argument(
        "file",
        type=str,
        nargs="?",
        default=None,
        help="Path to a single file which shall be checked. If file is '-', a list of files is "
        "read from stdin",
    )
    parser.add_argument(
        "-p",
        "--process",
        type=int,
        default=1,
        required=False,
        help="Set the number of process to use while processing files specified with '-' ",
    )

    _args = parser.parse_args(args)
    if not (_args.all or _args.file):
        parser.print_usage()
        return None
    return _args


def main(cmd_args: Sequence[str] | None = None):
    """
    The main function of this project. Parses the commandline, then creates and
    starts MCDCTreeChecker instances for each file to check.
    """
    _report = Report()
    args = _parse_args(cmd_args)

    if args is None:
        return McdcExit.INVALID_ARG.value
    if args.include:
        args.include = [include for include_list in args.include for include in include_list]
    if args.define:
        args.define = [define for define_list in args.define for define in define_list]
    if args.options:
        args.options = [option for option_list in args.options for option in option_list]

    files_to_check = []

    if args.all:
        for ext in ("c", "cc", "cxx", "cpp", "c++", "h", "hh", "hxx", "hpp", "h++"):
            files_to_check += glob(f"**/*.{ext}", recursive=True)
    elif args.file:
        if args.file == "-":
            files_to_check = [f.strip() for f in sys.stdin]
        else:
            files_to_check = [args.file]

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.process) as executor:
        futures = [
            executor.submit(
                check_file,
                f,
                args.include,
                args.define,
                args.options,
                args.debug,
            )
            for f in files_to_check
        ]
        concurrent.futures.wait(futures)
        for future in concurrent.futures.as_completed(futures):
            _report.merge(future.result())

    _report.print_statistics()
    _report.print_error_summary()

    if args.json_output:
        _report.save_json_report(args.json_output)

    for _, error_list in _report.errors.items():
        if len(error_list) > 0:
            return McdcExit.ERROR_FILES.value
    return McdcExit.NO_ERROR.value


if __name__ == "__main__":
    sys.exit(main())
