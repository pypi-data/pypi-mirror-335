import sys
from functools import partial

import gdsfactory as gf
import numpy as np
from gdsfactory.cross_section import get_cross_sections
from gdsfactory.technology import (
    LayerLevel,
    LayerMap,
    LayerStack,
    LayerViews,
)
from gdsfactory.typings import Layer

from hhi.config import PATH

nm = 1e-3


class LayerMapHHI(LayerMap):
    WG: Layer = (12, 0)  # 2µm passive waveguide
    E200: Layer = (13, 0)  # window; 42um wide 200µm deep etch window
    E600: Layer = (16, 0)  # window 42um wide 600µm deep etch window
    E1700: Layer = (18, 0)  # window 42um wide 1700µm deep etch window
    M1: Layer = (52, 0)  # M2 - 2um, butt-ended
    M2: Layer = (54, 0)  # defines the width
    BB_outline: Layer = (55, 0)  # defines BB placement
    BB_parameter: Layer = (56, 0)  # label with BB parameters
    BB_text: Layer = (59, 0)  # BB annotations
    FLOORPLAN: Layer = (
        7,
        0,
    )  # for wafer outline, and also for exclusion area cleave edge +/-50µm.
    TEXT: Layer = (24, 0)  # text and logos
    ISO: Layer = (51, 0)  # M2 + 2um, butt-ended

    # convenience layer names for generic PDK
    MTOP: Layer = (54, 0)  # defines the width


class Tech:
    width_e200 = 2.0
    width_e600 = 2.1
    width_e1700 = 2.3
    width_m2 = 12
    width_m1 = 12 + 4

    gap_m1 = 12
    gap_m2 = 16


TECH = Tech()
LAYER = LayerMapHHI


port_types_electrical = (
    "electrical",
    "electrical",
)
layer_label = LAYER.BB_parameter
layer_bbox = LAYER.BB_outline

################################################
# Cross-sections
################################################
xsection = gf.xsection


# Optical routing
@xsection
def E200() -> gf.CrossSection:
    s0 = gf.Section(layer=LAYER.WG, width=Tech.width_e200, port_names=("o1", "o2"))
    return gf.CrossSection(
        sections=(s0, gf.Section(layer=LAYER.E200, width=40)),
        radius=10e3,
    )


@xsection
def E600() -> gf.CrossSection:
    s0 = gf.Section(layer=LAYER.WG, width=Tech.width_e600, port_names=("o1", "o2"))
    return gf.CrossSection(
        sections=(s0, gf.Section(layer=LAYER.E600, width=40)),
        radius_min=450,
        radius=500.0,
    )


@xsection
def E1700() -> gf.CrossSection:
    s0 = gf.Section(layer=LAYER.WG, width=Tech.width_e1700, port_names=("o1", "o2"))
    return gf.CrossSection(
        sections=(s0, gf.Section(layer=LAYER.E1700, width=40)),
        radius_min=250,
        radius=300.0,
    )


@xsection
def ACT() -> gf.CrossSection:
    s0 = gf.Section(layer=LAYER.WG, width=2.1, port_names=("o1", "o2"))
    return gf.CrossSection(sections=(s0,))


@xsection
def FACET() -> gf.CrossSection:
    s0 = gf.Section(layer=LAYER.WG, width=2.1, port_names=("o1", "o2"))
    return gf.CrossSection(sections=(s0,))


def xs_metal(
    section_width: tuple[float, ...],
    width: float | None = None,
    gap: float | None = None,
    radius: float = 50,
    **kwargs,
) -> gf.CrossSection:
    """HHI metal tracks (shorthand). Adds isolation correctly.
    Please change if there is a more gdsfactoresque way to do this.
    Will use a signal track for ports. This is important to remember for GS tracks!

    Args:
        section_width: width(s) of the metal tracks
        width: This is just a dummy argument to avoid a BUG in gdsfactory8 with multi-section cross-sections
        gap: gap(s) between the metal tracks
    """

    if not hasattr(section_width, "__iter__"):
        section_width = (section_width,)
    if not hasattr(gap, "__iter__"):
        gap = (gap,) if gap else (0,) * (len(section_width) - 1)

    # Calculate corresponding offsets from gap & section_width
    total_width = sum(section_width) + sum(gap) if gap else sum(section_width)
    offsets = [0]
    if len(section_width) > 1:
        offsets = [
            -(total_width / 2)
            + sum(section_width[:i])
            + sum(gap[:i])
            + section_width[i] / 2
            for i in range(len(section_width))
        ]

    sections = []

    # If GSG or GS or any other multi-track, add the underlying isolation layer first
    # -> needed in gdsfactory 8 to avoid a BUG
    if len(section_width) > 1:
        sections.append(gf.Section(layer=LAYER.ISO, width=total_width + 4))

    # Create the metal sections
    for ww, (w, offset) in enumerate(zip(section_width, offsets)):
        # Only give ports to the central track, or the first track if there are only 1 or 2 tracks
        port_names = (
            ("e1", "e2")
            if (offset == 0 or (len(section_width) == 2 and ww == 1))
            else (None, None)
        )
        sections.extend(
            [
                gf.Section(
                    layer=LAYER.M1,
                    width=w,
                    offset=offset,
                    port_names=port_names,
                    port_types=("electrical", "electrical"),
                ),
                gf.Section(layer=LAYER.M2, width=w - 4, offset=offset),
            ]
        )

    # If single track, add the isolation layer at the end
    if len(section_width) == 1:
        sections.append(gf.Section(layer=LAYER.ISO, width=total_width + 4))

    return gf.CrossSection(sections=sections, radius=radius, **kwargs)


# Define the metal routing cross-sections


@xsection
def DC(section_width: float = TECH.width_m1, **kwargs) -> gf.CrossSection:
    """HHI metal tracks for DC routing.

    Args:
        section_width: width of the metal tracks

    """
    return xs_metal(section_width=section_width, **kwargs)


@xsection
def GS(
    section_width: tuple[float, ...] = (150, 150), gap: float = 24, radius=500, **kwargs
) -> gf.CrossSection:
    """HHI metal tracks for GS routing. Adds isolation correctly.

    Args:
        section_width: width(s) of the metal tracks
        gap: gap between the metal tracks
        radius: bend radius
    """
    return xs_metal(section_width=section_width, gap=gap, radius=radius, **kwargs)


@xsection
def GSG(
    section_width: tuple[float, ...] = (100, 60, 100),
    gap: tuple[float, ...] = (50, 50),
    radius=500,
    **kwargs,
) -> gf.CrossSection:
    """HHI metal tracks for GSG routing. Adds isolation correctly.

    Args:
        section_width: width(s) of the metal tracks
        gap: gap(s) between the metal tracks
        radius: bend radius
    """
    return xs_metal(section_width=section_width, gap=gap, radius=radius, **kwargs)


@xsection
def GSG_ground(section_width=100.0, radius=500, **kwargs) -> gf.CrossSection:
    return xs_metal(section_width=section_width, radius=radius, **kwargs)


@xsection
def GSG_signal(section_width=60.0, radius=500, **kwargs) -> gf.CrossSection:
    return xs_metal(section_width=section_width, radius=radius, **kwargs)


@xsection
def GS_ground(section_width=150.0, radius=500, **kwargs) -> gf.CrossSection:
    return xs_metal(section_width=section_width, radius=radius, **kwargs)


@xsection
def GS_signal(section_width=150.0, radius=500, **kwargs) -> gf.CrossSection:
    return xs_metal(section_width=section_width, radius=radius, **kwargs)


@xsection
def RF(section_width=100.0, radius=500, **kwargs) -> gf.CrossSection:
    return xs_metal(section_width=section_width, radius=radius, **kwargs)


@xsection
def RF_ground(section_width=150.0, radius=500, **kwargs) -> gf.CrossSection:
    return xs_metal(section_width=section_width, radius=radius, **kwargs)


@xsection
def RF_signal(section_width=150.0, radius=500, **kwargs) -> gf.CrossSection:
    return xs_metal(section_width=section_width, radius=radius, **kwargs)


cross_sections = get_cross_sections(sys.modules[__name__])

################################################
# Routing functions
################################################

route_single_e200 = partial(gf.routing.route_single, cross_section=E200)
route_single_e600 = partial(gf.routing.route_single, cross_section=E600)
route_single_e1700 = partial(gf.routing.route_single, cross_section=E1700)
route_single_dc = partial(gf.routing.route_single, cross_section=DC)
route_single_gs = partial(gf.routing.route_single, cross_section=GS)
route_single_gsg = partial(gf.routing.route_single, cross_section=GSG)
route_single_rf = partial(gf.routing.route_single, cross_section=RF)

route_single_sbend_e200 = partial(gf.routing.route_single_sbend, cross_section=E200)
route_single_sbend_e600 = partial(gf.routing.route_single_sbend, cross_section=E600)
route_single_sbend_e1700 = partial(gf.routing.route_single_sbend, cross_section=E1700)
route_single_sbend_dc = partial(gf.routing.route_single_sbend, cross_section=DC)
route_single_sbend_gs = partial(gf.routing.route_single_sbend, cross_section=GS)
route_single_sbend_gsg = partial(gf.routing.route_single_sbend, cross_section=GSG)
route_single_sbend_rf = partial(gf.routing.route_single_sbend, cross_section=RF)

route_bundle_e200 = partial(gf.routing.route_bundle, cross_section=E200)
route_bundle_e600 = partial(gf.routing.route_bundle, cross_section=E600)
route_bundle_e1700 = partial(gf.routing.route_bundle, cross_section=E1700)
route_bundle_dc = partial(gf.routing.route_bundle, cross_section=DC)
route_bundle_gs = partial(gf.routing.route_bundle, cross_section=GS)
route_bundle_gsg = partial(gf.routing.route_bundle, cross_section=GSG)
route_bundle_rf = partial(gf.routing.route_bundle, cross_section=RF)


route_bundle_sbend_e200 = partial(gf.routing.route_bundle_sbend, cross_section=E200)
route_bundle_sbend_e600 = partial(gf.routing.route_bundle_sbend, cross_section=E600)
route_bundle_sbend_e1700 = partial(gf.routing.route_bundle_sbend, cross_section=E1700)
route_bundle_sbend_dc = partial(gf.routing.route_bundle_sbend, cross_section=DC)
route_bundle_sbend_gs = partial(gf.routing.route_bundle_sbend, cross_section=GS)
route_bundle_sbend_gsg = partial(gf.routing.route_bundle_sbend, cross_section=GSG)
route_bundle_sbend_rf = partial(gf.routing.route_bundle_sbend, cross_section=RF)


################################################
# LayerStack
################################################
LAYER_VIEWS = LayerViews(PATH.lyp_yaml)
constants = {
    "fiber_array_spacing": 127.0,
    "fiber_spacing": 50.0,
    "fiber_input_to_output_spacing": 200.0,
    "metal_spacing": 30.0,
    "pad_pitch": 150.0,
    "pad_size": (66, 66),
}


# Define the layer stack
bias_E1700 = -150 * nm + 70 * nm  # second value to compensate
sidewall_angle = 5  # [°]

# TODO:Integrate these values into the layer stack
etch_depth_E1700 = 1850 * nm
etch_depth_E200 = 300 * nm
etch_depth_E600 = 650 * nm

layer_thicknesses = {
    "Substrate": 10000 * nm,
    "E1700_1": 100 * nm,
    "E1700_2": 700 * nm,
    "E1700_3": 820 * nm,
    "E1700_4": 20 * nm,
    "E1700_5": 205 * nm,
    "E1700_6": 5 * nm,
    "E1700_7": 50 * nm,
}


def get_layer_stack(
    layer_thicknesses: dict = layer_thicknesses,
    etch_depth_E1700: float = etch_depth_E1700,
    sidewall_angle: float = sidewall_angle,
) -> LayerStack:
    """Returns LayerStack."""

    layers = dict(
        Substrate=LayerLevel(
            layer=LAYER.E1700,
            thickness=layer_thicknesses["Substrate"],
            zmin=0,
            material="InP",
            mesh_order=1,
            sidewall_angle=0,
        ),
        E1700_1=LayerLevel(
            layer=LAYER.WG,
            thickness=layer_thicknesses["E1700_1"],
            zmin=layer_thicknesses["Substrate"],
            material="Q(1.06)",
            mesh_order=2,
            sidewall_angle=sidewall_angle,
            bias=bias_E1700,
        ),
        E1700_2=LayerLevel(
            layer=LAYER.WG,
            thickness=layer_thicknesses["E1700_2"],
            zmin=layer_thicknesses["Substrate"] + layer_thicknesses["E1700_1"],
            material="InP",
            mesh_order=3,
            sidewall_angle=sidewall_angle,
            bias=bias_E1700
            - layer_thicknesses["E1700_1"] / np.tan(np.deg2rad(90 - sidewall_angle)),
        ),
        E1700_3=LayerLevel(
            layer=LAYER.WG,
            thickness=layer_thicknesses["E1700_3"],
            zmin=layer_thicknesses["Substrate"]
            + layer_thicknesses["E1700_1"]
            + layer_thicknesses["E1700_2"],
            material="Q(1.06)",
            mesh_order=4,
            sidewall_angle=sidewall_angle,
            bias=bias_E1700
            - layer_thicknesses["E1700_1"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_2"] / np.tan(np.deg2rad(90 - sidewall_angle)),
        ),
        E1700_4=LayerLevel(
            layer=LAYER.WG,
            thickness=layer_thicknesses["E1700_4"],
            zmin=layer_thicknesses["Substrate"]
            + layer_thicknesses["E1700_1"]
            + layer_thicknesses["E1700_2"]
            + layer_thicknesses["E1700_3"],
            material="InP",
            mesh_order=5,
            sidewall_angle=sidewall_angle,
            bias=bias_E1700
            - layer_thicknesses["E1700_1"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_2"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_3"] / np.tan(np.deg2rad(90 - sidewall_angle)),
        ),
        E1700_5=LayerLevel(
            layer=LAYER.WG,
            thickness=layer_thicknesses["E1700_5"],
            zmin=layer_thicknesses["Substrate"]
            + layer_thicknesses["E1700_1"]
            + layer_thicknesses["E1700_2"]
            + layer_thicknesses["E1700_3"]
            + layer_thicknesses["E1700_4"],
            material="Q(1.06)",
            mesh_order=6,
            sidewall_angle=sidewall_angle,
            bias=bias_E1700
            - layer_thicknesses["E1700_1"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_2"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_3"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_4"] / np.tan(np.deg2rad(90 - sidewall_angle)),
        ),
        E1700_6=LayerLevel(
            layer=LAYER.WG,
            thickness=layer_thicknesses["E1700_6"],
            zmin=layer_thicknesses["Substrate"]
            + layer_thicknesses["E1700_1"]
            + layer_thicknesses["E1700_2"]
            + layer_thicknesses["E1700_3"]
            + layer_thicknesses["E1700_4"]
            + layer_thicknesses["E1700_5"],
            material="InP",
            mesh_order=7,
            sidewall_angle=sidewall_angle,
            bias=bias_E1700
            - layer_thicknesses["E1700_1"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_2"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_3"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_4"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_5"] / np.tan(np.deg2rad(90 - sidewall_angle)),
        ),
        E1700_7=LayerLevel(
            layer=LAYER.WG,
            thickness=layer_thicknesses["E1700_7"],
            zmin=layer_thicknesses["Substrate"]
            + layer_thicknesses["E1700_1"]
            + layer_thicknesses["E1700_2"]
            + layer_thicknesses["E1700_3"]
            + layer_thicknesses["E1700_4"]
            + layer_thicknesses["E1700_5"]
            + layer_thicknesses["E1700_6"],
            material="sin",
            mesh_order=8,
            sidewall_angle=sidewall_angle,
            bias=bias_E1700
            - layer_thicknesses["E1700_1"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_2"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_3"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_4"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_5"] / np.tan(np.deg2rad(90 - sidewall_angle))
            - layer_thicknesses["E1700_6"] / np.tan(np.deg2rad(90 - sidewall_angle)),
        ),
    )

    return LayerStack(layers=layers)


LAYER_STACK = get_layer_stack()


MATERIALS_INDEX = {  # this is a placeholder.
    # We have very accurate material models, but still unclear how to implement them here
    "InP": 3.167,
    "Q(1.06)": 3.258,
    "sin": 2.0,
}

if __name__ == "__main__":
    c = gf.components.straight(cross_section=E200)
    c = gf.components.straight(cross_section=E600)
    c = gf.components.straight(cross_section=E1700)
    c.show()
    # s = c.to_3d()
    # s.show()
