# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Lambda expression for filtering a dict according to a list of keys."""

import csv
from collections import OrderedDict
from collections.abc import Sequence

from tabulate import tabulate


def _dictfilt(x, y):
    return OrderedDict([(i, x[i]) for i in x if i in set(y)])


class TableExporter:
    """Exporter table to a file."""

    @staticmethod
    def export_to_file(
        table_dict: list[dict],
        headers: dict[str, str] | Sequence[str] | list[str],
        file="result.md",
    ) -> None:
        """Export the listed entries to a specified file."""
        temp_dict = []
        if isinstance(headers, list):
            # Filter into new dict
            for elem in table_dict:
                temp_dict.append(_dictfilt(elem, headers))
            # Reorder keys according to headers
            for elem in temp_dict:
                for header_name in reversed(headers):
                    if elem.get(header_name):
                        elem.move_to_end(header_name)
            temp_headers = "keys"

        else:
            temp_dict = table_dict
            temp_headers = headers

        with open(file, "w", encoding="utf-8") as _fp:
            if file.endswith(".md"):
                _fp.write(tabulate(temp_dict, headers=temp_headers, tablefmt="pipe"))
            if file.endswith(".tex"):
                _fp.write(tabulate(temp_dict, headers=temp_headers, tablefmt="latex"))
            if file.endswith(".html"):
                _fp.write(tabulate(temp_dict, headers=temp_headers, tablefmt="html"))
            if file.endswith(".csv"):
                writer = csv.DictWriter(_fp, fieldnames=headers)
                writer.writeheader()
                writer.writerows(temp_dict)
