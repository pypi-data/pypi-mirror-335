"""SAX Simulation functions."""

from collections.abc import Callable
from typing import Literal

from pandas import DataFrame
from pydantic import validate_call
from sax.netlist import RecursiveNetlist
from sax.saxtypes import Model

from .core.simulate import circuit as _circuit
from .core.simulate import circuit_df as _circuit_df
from .core.simulate import circuit_plot as _circuit_plot
from .settings import SETTINGS


@validate_call
def circuit(
    netlist: RecursiveNetlist,
    pdk: str = SETTINGS.pdk.name,
    host: str = SETTINGS.sim.host,
    api_key: str = SETTINGS.api.key,
) -> Model:
    """Create a sax circuit with dosax backend."""
    return _circuit(netlist, pdk, host, api_key)


@validate_call
def circuit_df(
    netlist: RecursiveNetlist,
    pdk: str = SETTINGS.pdk.name,
    host: str = SETTINGS.sim.host,
    api_key: str = SETTINGS.api.key,
) -> Callable[..., DataFrame]:
    """Create a sax circuit with dosax backend."""
    return _circuit_df(netlist, pdk, host, api_key)


@validate_call
def circuit_plot(
    netlist: RecursiveNetlist,
    pdk: str = SETTINGS.pdk.name,
    host: str = SETTINGS.sim.host,
    api_key: str = SETTINGS.api.key,
    op: str = "dB",
    port_in: str = "",
    which: Literal["html", "json"] = "html",
) -> Callable[..., dict | str]:
    """Create a sax circuit with dosax backend."""
    return _circuit_plot(
        netlist=netlist,
        pdk=pdk,
        host=host,
        api_key=api_key,
        op=op,
        port_in=port_in,
        which=which,
    )
