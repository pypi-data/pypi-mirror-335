from functools import partial

import gdsfactory as gf
import numpy as np

from hhi.cells import (
    HHI_DFB,
    HHI_SSCLATE1700,
    HHI_MMI1x2E600,
    HHI_MMI1x2E1700,
    HHI_MMI2x2E600,
    HHI_MMI2x2E1700,
)
from hhi.tech import LAYER

pad = partial(
    gf.c.pad,
    size=(66, 66),
    layer=LAYER.M2,
    bbox_layers=(LAYER.M1, LAYER.ISO),
    bbox_offsets=(2, 2),
)


@gf.cell
def cleave_mark() -> gf.Component:
    c = gf.Component(name="cleave_mark")
    c.add_polygon([[0.0, 0.0], [15.442, 33.12], [33.119, 15.441]], layer=LAYER.TEXT)
    return c


@gf.cell
def die(size=(8000, 4000), centered=False) -> gf.Component:
    """Create a die template with cleave marks"""
    c = gf.Component()

    allowed_sizes = (
        np.array(
            [
                (1, 1),
                (1, 2),
                (1, 4),
                (1, 6),
                (1, 8),
                (2, 1),
                (2, 2),
                (2, 4),
                (2, 6),
                (4, 1),
                (8, 1),
                (2, 2),
                (4, 2),
                (8, 2),
                (12, 2),
                (4, 4),
                (8, 4),
                (12, 4),
                (1, 8),
                (2, 8),
                (3, 8),
                (4, 8),
                (1, 12),
                (12, 12),
                (2, 12),
                (3, 12),
                (4, 12),
                (8, 24),
            ]
        )
        * 1000
    )

    # Check size is in the available sizes
    if not any(np.allclose(size, s) for s in allowed_sizes):
        raise ValueError(f"Size must be one of {np.round(allowed_sizes * 1e-3)} mm")
    # Add the BB exclusion zone, demarking the chip boundary
    die = c << gf.components.die(size=size, street_width=50, die_name="")
    if not centered:
        die.dmovex(size[0] / 2)
        die.dmovey(size[1] / 2)

    # Add the 4 cleave marks in each corner
    for corner, p2 in zip(
        [(0, 0), (0, 1), (1, 0), (1, 1)], [(1, 1), (1, 0), (0, 1), (1, -1)]
    ):
        cm = c << cleave_mark()
        p1 = (0, 0)
        p2 = (p2[0], p2[1])
        cm.dmirror(p1=p1, p2=p2)
        cm.dmovex(corner[0] * size[0] - size[0] / 2 * (centered))
        cm.dmovey(corner[1] * size[1] - size[1] / 2 * (centered))

    return c


@gf.cell
def die_rf(
    size=(8000, 4000),
    num_dc_pads: int = 23,
    dc_pad_pitch=150,
    dc_pad_size=(98, 138),
    num_rf_pads: int = 8,
    rf_pad_sizex=98.0,
    rf_pad_pitch=136,
    rf_pad_pos=(100, 250),
    num_SSCs: int = 10,
    ssc=HHI_SSCLATE1700,
) -> gf.Component:
    """Create a template for RF connections.
    # TODO: Add the RF connections, text labels, design region, etc.

    Args:
        size: Size of the die.
        num_dc_pads: Number of DC pads.
        dc_pad_pitch: Spacing between DC pads.
        dc_pad_size: Size of the DC pads.
        num_rf_pads: Number of RF pads.
        rf_pad_sizex: Size of the RF pads in the x-direction.
        rf_pad_pitch: Spacing between RF pads.
        rf_pad_pos: Position of the RF pads.
        num_SSCs: Number of spot size converters SSCs.
        ssc: SSC component.
    """
    c = gf.Component()

    # Fixed parameters
    id_pos = (size[0] - 150, 150)
    dc_pad_pos1 = (3231, size[1] - 114 - dc_pad_size[1] / 2)
    dc_pad_pos2 = (3231, 114 + dc_pad_size[1] / 2)

    ssc = gf.get_component(ssc)

    SSCs_pos = (size[0] - ssc.dxsize / 2, size[1] / 2)
    SSCs_spacing = 127

    _ = c << die(size=size)

    # Add HHI_ID cell square
    HHI_ID = gf.components.rectangle(
        size=(100, 100), layer="BB_outline", centered=True, port_type=None
    ).dup()
    HHI_ID.name = "HHI_ID"
    hhi_id = c << HHI_ID
    hhi_id.dmove(id_pos)

    # Add the DC pads at the top
    for dc_pad_pos in [dc_pad_pos1, dc_pad_pos2]:
        dc_pads = c << gf.components.array(
            pad(size=dc_pad_size), column_pitch=dc_pad_pitch, columns=num_dc_pads
        )
        dc_pads.dmove(dc_pad_pos)
        c.add_ports(dc_pads.ports, prefix=["top_", "bot_"][(dc_pad_pos == dc_pad_pos2)])

    # Add the RF ports on the left side
    rf_pads = c << gf.components.straight_array(
        num_rf_pads, rf_pad_pitch, rf_pad_sizex, "GSG"
    )
    rf_pads.dmove(rf_pad_pos)
    rf_ports = rf_pads.ports.filter(orientation=0)
    c.add_ports(rf_ports, prefix="rf_")

    # Add the SSCs at the right side
    sscs = c << gf.components.array(
        ssc,
        row_pitch=SSCs_spacing,
        columns=1,
        rows=num_SSCs,
        centered=True,
    )
    sscs.dmove(SSCs_pos)
    SSC_E1700_ports = gf.port.get_ports_list(sscs.ports, prefix="o1")
    c.add_ports(SSC_E1700_ports, prefix="SSC_")
    return c


# Straight definitions
straight = partial(gf.components.straight, cross_section="E1700")

# Bend definitions
bend_circular = partial(gf.components.bend_circular, cross_section="E1700")
bend_euler = partial(gf.components.bend_euler, cross_section="E1700")

add_pads_bot = partial(
    gf.routing.add_pads_bot,
    component=HHI_DFB,
    pad=pad,
    cross_section="DC",
    straight_separation=30,
    bend=bend_circular,
)
mzi_E1700 = partial(gf.components.mzi, cross_section="E1700", splitter=HHI_MMI1x2E1700)
mzi_E600 = partial(gf.components.mzi, cross_section="E600", splitter=HHI_MMI1x2E600)

mzi1x2_2x2_E1700 = partial(
    gf.components.mzi1x2_2x2,
    cross_section="E1700",
    splitter=HHI_MMI1x2E1700,
    combiner=HHI_MMI2x2E1700,
    port_e1_combiner="o2",
    port_e0_combiner="o4",
)
mzi1x2_2x2_E600 = partial(
    gf.components.mzi1x2_2x2,
    cross_section="E600",
    splitter=HHI_MMI1x2E600,
    combiner=HHI_MMI2x2E600,
    port_e1_combiner="o2",
    port_e0_combiner="o4",
)
array = gf.components.array
straight = partial(gf.components.straight, cross_section="E1700")
bend_s = partial(gf.components.bend_s, cross_section="E1700", size=(50, 1.5))
taper_dc = partial(
    gf.components.taper,
    cross_section="DC",
    port_types=("electrical", "electrical"),
    port_names=("e1", "e2"),
)


if __name__ == "__main__":
    c = bend_s()
    c.show()
