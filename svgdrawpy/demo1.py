from svgdrawpy import *

draw(
    [   
        Comm('示例-太极图'),
        Circle().by_c_r(
            ORIG,200
        ),
        Arc().by_circ_theta(
            Circle().by_c_r(
                Vec(0,100),100
            ),
            -90*deg,90*deg
        ),
        Circle().by_c_r(
            Vec(0,100),30
        ),
        Arc().by_circ_theta(
            Circle().by_c_r(
                Vec(0,-100),100
            ),
            90*deg,-90*deg
        ),
        Circle().by_c_r(
            Vec(0,-100),30
        ),

    ],
    filepath='./demo1.svg',viewbox="-500 -500 1000 1000"
)
