import gdsfactory as gf

from hhi import cells, tech
from hhi.cells2 import die, pad
from hhi.config import PATH

size1 = (2e3, 8e3)
size2 = (4e3, 8e3)
size3 = (12e3, 8e3)


@gf.cell
def sample_die(size=(8e3, 24e3), y_spacing: float = 40) -> gf.Component:
    """Returns a sample die

    Args:
        size: size of the die. Typical sizes are 2x8mm², 4x8mm² and 12x8mm².
        y_spacing: spacing between components.

    Returns:
        c: a sample die.

    .. plot::
      :include-source:

      import gdsfactory as gf
      from hhi.samples import demo

      c = demo.sample_die()
      c.draw_ports()
      c.plot()
    """
    c = gf.Component()

    rdie = c << die(size, centered=True)

    components = [
        cells.HHI_BJsingle,
        cells.HHI_BJtwin,
        cells.HHI_BPD,
        cells.HHI_DBR,
        cells.HHI_DBRsection,
        cells.HHI_DFB,
        cells.HHI_DFBsection,
        cells.HHI_DirCoupE1700,
        cells.HHI_DirCoupE600,
        cells.HHI_EAM,
        cells.HHI_EAMsection,
        cells.HHI_EOElectricalGND,
        cells.HHI_EOPMTermination,
        cells.HHI_GRAT,
        cells.HHI_GRATsection,
        cells.HHI_GSGtoGS,
        cells.HHI_ISOsectionSingle,
        cells.HHI_ISOsectionTwin,
        cells.HHI_METMETx,
        cells.HHI_MIR1E1700,
        cells.HHI_MIR2E1700,
        cells.HHI_MMI1x2ACT,
        cells.HHI_MMI1x2E1700,
        cells.HHI_MMI1x2E600,
        cells.HHI_MMI2x2ACT,
        cells.HHI_MMI2x2E1700,
        cells.HHI_MMI2x2E600,
        cells.HHI_MZIswitch,
        cells.HHI_MZMDD,
        cells.HHI_MZMDU,
        cells.HHI_PDDC,
        cells.HHI_PDRFsingle,
        cells.HHI_PDRFtwin,
        cells.HHI_PMTOE1700,
        cells.HHI_PMTOE200,
        cells.HHI_PMTOE600,
        cells.HHI_PolConverter45,
        cells.HHI_PolConverter90,
        cells.HHI_PolSplitter,
        cells.HHI_R50GSG,
        cells.HHI_SGDBRTO,
        cells.HHI_SOA,
        cells.HHI_SOAsection,
        cells.HHI_TOBiasSection,
        cells.HHI_WGMETxACTGSGsingle,
        cells.HHI_WGMETxACTGSGtwin,
        cells.HHI_WGMETxACTGSsingle,
        cells.HHI_WGMETxACTGStwin,
        cells.HHI_WGMETxACTsingle,
        cells.HHI_WGMETxACTtwin,
        cells.HHI_WGMETxE1700GSGsingle,
        cells.HHI_WGMETxE1700GSGtwin,
        cells.HHI_WGMETxE1700GSsingle,
        cells.HHI_WGMETxE1700GStwin,
        cells.HHI_WGMETxE1700single,
        cells.HHI_WGMETxE1700twin,
        cells.HHI_WGMETxE200,
        cells.HHI_WGMETxE200GS,
        cells.HHI_WGMETxE200GSG,
        cells.HHI_WGMETxE600,
        cells.HHI_WGMETxE600GS,
        cells.HHI_WGMETxE600GSG,
        cells.HHI_WGTE200E1700,
        cells.HHI_WGTE200E600,
        cells.HHI_WGTE600E1700,
    ]
    ymin = rdie.dymin + 100

    # This is spaghetti code to map the cross-sections to the correct FACET BB cells
    ecdict = {
        tech.E1700: cells.HHI_FacetWGE1700,
        "E1700twin": cells.HHI_FacetWGE1700twin,
        tech.E600: cells.HHI_FacetWGE600,
        tech.E200: cells.HHI_FacetWGE200,
        tech.ACT: cells.HHI_ISOsectionSingle,  # Not really a FACET BB cell
        "ACTtwin": cells.HHI_ISOsectionTwin,
    }

    for component in components:
        ci = component()
        ci = (
            gf.routing.add_pads_bot(
                ci,
                cross_section="DC",
                straight_separation=10,
                bend="bend_circular",
                pad=pad,
                pad_pitch=150,
                force_manhattan=True,
            )
            if ci.ports.filter(port_type="electrical")
            else ci
        )
        ref = c << ci
        ref.dymin = ymin
        ref.dx = 0
        ymin = ref.dymax + y_spacing

        # get the optical ports of the component
        oports_left = ref.ports.filter(orientation=180)
        oports_right = ref.ports.filter(orientation=0)

        ### Routing to L facet

        # The `add_pads_bot` function leaves only optical ports in `ref`
        xsec = (
            tech.cross_sections[oports_left[0].info["cross_section"]]
            if oports_left
            else tech.E1700
        )
        ec = ecdict[xsec]()
        if xsec == tech.ACT:
            xlength_left = oports_left[0].dx - rdie.dxmin + 50
            ec = (
                ecdict["ACTtwin"](L_I=xlength_left)
                if len(oports_left) == 2
                else ecdict[tech.ACT](L_I=xlength_left)
            )
            # xsec = 'ACT' # TODO: find some way to allow HHI_ISOsection(Twin) to be used as a cross-section

        # if xsec == tech.E1700 and len(oports_left) == 2: # won't work
        #     ec   = ecdict['E1700twin']()

        routes_left, ports_left = gf.routing.route_ports_to_side(
            component=c,
            ports=oports_left,
            cross_section=xsec,
            side="west",
            x=rdie.dxmin + ec.xsize - 50.001 * (xsec == tech.ACT),
        )

        if oports_left:
            for p in ports_left:
                ref = c << ec
                ref.connect("o1", p)
                if "twin" in ec.name.lower():
                    break

            text = c << gf.c.text(
                text=f"{component().name}-{'+'.join([p.name.split('_')[0] for p in ports_left])}",
                size=30,
                layer="TEXT",
            )
            text.dxmin = ref.dxmin + 105
            text.dy = ref.dymax + 20

        ### Routing to R facet
        xsec = (
            tech.cross_sections[oports_right[0].info["cross_section"]]
            if oports_right
            else tech.E1700
        )
        ec = ecdict[xsec]()
        if xsec == tech.ACT:
            xlength_left = rdie.dxmax - oports_right[0].dx + 50
            ec = (
                ecdict["ACTtwin"](L_I=xlength_left)
                if len(oports_left) == 2
                else ecdict[tech.ACT](L_I=xlength_left)
            )

        routes_right, ports_right = gf.routing.route_ports_to_side(
            component=c,
            ports=oports_right,
            cross_section=xsec,
            x=rdie.dxmax - ec.xsize + 50.001 * (xsec == tech.ACT),
            side="east",
        )

        ports_right.sort(key=lambda p: p.y, reverse=True)
        if oports_right:
            for p in ports_right:
                ref = c << ec
                ref.connect("o1", p)
                if "twin" in ec.name.lower():
                    break
            text = c << gf.c.text(
                text=f"{component().name}-{'+'.join([p.name.split('_')[0] for p in ports_right])}",
                size=30,
                layer="TEXT",
            )
            text.dxmax = ref.dxmax - 105
            text.dy = ref.dymax + 20

    # Rename all cells to remove the `:`, `,` characters
    for cell in c.get_dependencies(True):
        cell.name = cell.name.replace(":", "_").replace(",", "_")

    return c


if __name__ == "__main__":
    c = sample_die()
    # c = cells.HHI_MZIswitch()
    # p = c['o1']
    c.write_gds(gdspath=PATH.extra / "sample_die.gds")
    c.show()
