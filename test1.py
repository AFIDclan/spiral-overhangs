from LayerList import Layer
from LayerList import Position
from LayerList import LayerList
from Helpers import *
import numpy as np
import math
import copy

ll = LayerList.FromFile("dome2.gcode")

start_layers = ll.layers[0:10]
end_layers = ll.layers[-1:]




layer_height = 0.2
arc_start_angle = 0

ret, circle_center, circle_radius, start_angle = fit_circle(start_layers[-1])


arc_gen = ArcGenerator(math.pi/3, circle_radius, layer_height)

circle_steps = 100
layers=[]
term = False
step_nums = 0

initial_offset = None
while not term:
    term, R, offset = arc_gen.step()

    if term:
        break

    step_nums += 1
    if (initial_offset is None):
        initial_offset = offset
        
    offset = offset - initial_offset

    
    #Create a circle of positions around the center
    layer = Layer()
    layer.lines = [] # Needed to clear the lines from the previous layer. NO idea why we need this.
    for i in range(circle_steps):
        ang = i/circle_steps*2*np.pi
        ang = ang + start_angle
        pos = Position()
        pos.x = circle_center[0] + R*np.cos(ang)
        pos.y = circle_center[1] + R*np.sin(ang)
        pos.z = circle_center[2] + offset
        layer.add(pos)
    layer.add_terminator()
    layers.append(layer)


ll_out = LayerList(start_layers+layers+end_layers)


with open("out2.gcode", 'w') as f:
    f.write(ll_out.render())