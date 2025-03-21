"""Test Component Builds."""

import sys
from collections.abc import Generator
from functools import cache

import gdsfactory as gf
import pytest
import typer

from gdsfactoryplus.cli.app import app
from gdsfactoryplus.core.shared import activate_pdk_by_name
from gdsfactoryplus.project import maybe_find_docode_project_dir
from gdsfactoryplus.settings import SETTINGS

__all__ = ["do_test"]


@app.command(name="test")
def do_test() -> None:
    """Test if the cells in the project can be built."""
    project_dir = maybe_find_docode_project_dir()
    if project_dir is None:
        print(  # noqa: T201
            "Could not start tests. Please run tests inside a GDSFactory+ project.",
            file=sys.stderr,
        )
        raise typer.Exit(1)
    pytest.main(["-s", __file__])


@cache
def get_pdk() -> gf.Pdk:
    """Get the pdk."""
    return activate_pdk_by_name(SETTINGS.pdk.name)


def _iter_cells() -> Generator[str]:
    yield from get_pdk().cells


@pytest.mark.parametrize("cell_name", _iter_cells())
def test_build(cell_name: str) -> None:
    """Test if a cell can be built."""
    print(cell_name)  # noqa: T201
    func = get_pdk().cells[cell_name]
    func()
