from svgdrawpy import *

draw(
    [
        Comm('示例2-无标题'),
        Lines().extend(
            [
                rVec(200,i*2*pi/7)
                    for i in (0,2,4,6,1,3,5)
            ]
        ).set_is_close(True)
    ],
    filepath='./demo2.svg',
    viewbox='-300 -300 600 600'
)