from svgdrawpy import *


draw(
    [
        xyLines,
        xyLine,
        Vec('A').by_xy(0,200).out(),
        *[
            Group().include(
                Group().include(
                    Vec('A').rotate().set_name('B').out(),
                    Arc().by_2p_theta(
                        Vec('B'),Vec('A'),90*deg
                    ).set_name('arc'),
                    (
                        Line().by_theta_p(
                            90*deg+(i+1)*5*deg,ORIG
                        ) & Arc('arc')
                    ).set_name('A').out(),
                ).set_name(str(i)),
                Group(str(i)).rotate(pi/2,ORIG),
                Group(str(i)).rotate(pi,ORIG),
                Group(str(i)).rotate(3*pi/2,ORIG)
            )
            for i in range(8)
        ]
    ],
    filepath='./demo3.svg',
    viewbox='-300 -300 600 600'
)