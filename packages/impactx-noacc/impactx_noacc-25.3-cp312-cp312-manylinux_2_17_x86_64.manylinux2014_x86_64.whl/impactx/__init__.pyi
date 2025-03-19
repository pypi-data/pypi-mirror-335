"""

impactx_pybind
--------------
.. currentmodule:: impactx_pybind

.. autosummary::
   :toctree: _generate
   ImpactX
   distribution
   elements

"""

from __future__ import annotations

import os as os

from amrex import space3d as amr
from amrex.space3d.amrex_3d_pybind import SmallMatrix_6x6_F_SI1_double as Map6x6
from impactx.distribution_input_helpers import twiss
from impactx.extensions.ImpactXParticleContainer import (
    register_ImpactXParticleContainer_extension,
)
from impactx.impactx_pybind import (
    Config,
    CoordSystem,
    Envelope,
    ImpactX,
    ImpactXParConstIter,
    ImpactXParIter,
    ImpactXParticleContainer,
    RefPart,
    coordinate_transformation,
    create_envelope,
    distribution,
    elements,
    push,
    wakeconvolution,
)
from impactx.madx_to_impactx import read_beam, read_lattice

from . import (
    MADXParser,
    distribution_input_helpers,
    extensions,
    impactx_pybind,
    madx_to_impactx,
)

__all__ = [
    "Config",
    "CoordSystem",
    "Envelope",
    "ImpactX",
    "ImpactXParConstIter",
    "ImpactXParIter",
    "ImpactXParticleContainer",
    "MADXParser",
    "Map6x6",
    "RefPart",
    "amr",
    "coordinate_transformation",
    "create_envelope",
    "cxx",
    "distribution",
    "distribution_input_helpers",
    "elements",
    "extensions",
    "impactx_pybind",
    "madx_to_impactx",
    "os",
    "push",
    "read_beam",
    "read_lattice",
    "register_ImpactXParticleContainer_extension",
    "s",
    "t",
    "twiss",
    "wakeconvolution",
]
__author__: str = (
    "Axel Huebl, Chad Mitchell, Ryan Sandberg, Marco Garten, Ji Qiang, et al."
)
__license__: str = "BSD-3-Clause-LBNL"
__version__: str = "25.03"
s: impactx_pybind.CoordSystem  # value = <CoordSystem.s: 0>
t: impactx_pybind.CoordSystem  # value = <CoordSystem.t: 1>
cxx = impactx_pybind
