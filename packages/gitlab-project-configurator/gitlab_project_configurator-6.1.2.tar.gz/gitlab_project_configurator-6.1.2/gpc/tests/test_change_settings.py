# Standard Library
import re

# Third Party Libraries
import pytest

from rich.console import Console
from rich.table import Table

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangeSetting


SPACE = " "


@pytest.mark.parametrize(
    "before, after, expected",
    [
        (None, "something", "│ property_name │ None │ something │ added │"),
        (
            "something",
            "somethingelse",
            "│ property_name │ something │ somethingelse │ updated │",
        ),
    ],
)
def test_change_setting(before, after, expected):
    console = Console(record=True)
    table = Table()
    cs = ChangeSetting("property_name", before, after)
    for row in cs.rich_rows(console):
        if isinstance(row, str) and row == "new_line":
            table.add_row()
        elif isinstance(row, str) and row == "new_section":
            table.add_section()
        else:
            table.add_row(*row[0])

    console.print(table)
    rs = console.export_text()
    pattern = re.compile(r"\s+")
    rs = re.sub(pattern, " ", rs)
    assert expected in rs
