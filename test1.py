from LayerList import Layer
from LayerList import Position
from LayerList import LayerList
from Helpers import *
import numpy as np
import math

ll = LayerList.FromFile("dome2.gcode")

start_layers = ll.layers[0:10]
end_layers = ll.layers[-1:]




layer_height = 0.2
arc_start_angle = 0

ret, circle_center, circle_radius, start_angle = fit_circle(start_layers[-1])

circle_steps = 100

for u in range (160):

    arc_start_angle += 0.01

    circle_radius-= math.sin(arc_start_angle)*layer_height
    circle_center[2]+= math.cos(arc_start_angle)*layer_height

    layers=[]
    #Create a circle of positions around the center
    layer = Layer()
    for i in range(circle_steps):
        ang = i/circle_steps*2*np.pi
        ang = ang + start_angle
        pos = Position()
        pos.x = circle_center[0] + circle_radius*np.cos(ang)
        pos.y = circle_center[1] + circle_radius*np.sin(ang)
        pos.z = circle_center[2]
        layer.add(pos)
    layer.add_terminator()
    layers.append(layer)


ll_out = LayerList(start_layers+layers+end_layers)


with open("out2.gcode", 'w') as f:
    f.write(ll_out.render())