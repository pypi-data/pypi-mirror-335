"""hhi - HHI photonics PDK"""

import gdsfactory as gf
from gdsfactory.get_factories import get_cells

from hhi import cells, cells2, config
from hhi.models import models
from hhi.tech import (
    LAYER,
    LAYER_STACK,
    LAYER_VIEWS,
    MATERIALS_INDEX,
    constants,
    cross_sections,
)

cells_dict = get_cells([cells, cells2])

layer_transitions = {
    (LAYER.M1, LAYER.M2): "taper_dc",
    (LAYER.M2, LAYER.M1): "taper_dc",
}


PDK = gf.Pdk(
    name="HHI",
    cells=cells_dict,
    cross_sections=cross_sections,
    layers=LAYER,
    layer_stack=LAYER_STACK,
    layer_views=LAYER_VIEWS,
    layer_transitions=layer_transitions,
    materials_index=MATERIALS_INDEX,
    constants=constants,
    models=models,
)
PDK.activate()

__all__ = (
    "cells",
    "config",
    "PDK",
    "LAYER",
    "LAYER_VIEWS",
    "LAYER_STACK",
    "cross_sections",
    "constants",
)
__version__ = "0.2.4"
