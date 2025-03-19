# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Integration test for MCDC Checker
"""
import json
import os
from deepdiff import DeepDiff  # type: ignore[import-untyped]

from mcdc_checker.__main__ import main


def compare_json_files(file1, file2):
    """Compare two json files"""
    with (
        open(file1, mode="r", encoding="utf-8") as f1,
        open(file2, mode="r", encoding="utf-8") as f2,
    ):
        content1 = json.load(f1)
        content2 = json.load(f2)
        # Optional: ignore attribute "fingerprint" if necessary
        diff = DeepDiff(content1, content2, ignore_order=True)
    return diff


def test_mcdc_checker():
    """Test the complete application using the entry module"""
    command = [
        "-a",
        "-j",
        "result.json",
        "mcdc_checker/tests/main.c",
    ]
    main(command)

    diff = compare_json_files("./result.json", "./mcdc_checker/tests/main.c.json")
    assert len(diff) == 0, diff

    os.system("rm file_mcdc_checker-tests-*.dot")
    os.system("rm result.json")
