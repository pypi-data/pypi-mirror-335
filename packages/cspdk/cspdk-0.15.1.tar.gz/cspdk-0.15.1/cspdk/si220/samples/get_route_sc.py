"""`route_single` returns a Manhattan route between two ports."""

import gdsfactory as gf

from cspdk.si220 import cells, tech

if __name__ == "__main__":
    c = gf.Component("sample_connect")
    mmi1 = c << cells.mmi1x2_sc()
    mmi2 = c << cells.mmi1x2_sc()
    mmi2.dmove((500, 50))

    route = tech.route_single_sc(
        c,
        mmi1.ports["o3"],
        mmi2.ports["o1"],
    )
    c.show()
