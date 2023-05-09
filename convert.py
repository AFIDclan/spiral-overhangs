from LayerList import *
from Helpers import *
import numpy as np
import math
import copy

file="dome2"

ll = LayerList.FromFile(file+".gcode")

# -- SELECT WHICH LAYERS TO KEEP AT BEGINNING AND END --
start_layers = ll.layers[0:10]
end_layers = ll.layers[-1:]



extrude_mm_per_mm = 0.06281503928279897
layer_height = 0.4
extrude_temp = 185
min_seconds_per_circle = 15


# -- SELECT LAYER TO CIRCLE FIT --
ret, circle_center, circle_radius, start_angle = fit_circle(start_layers[-1])


# Generate a dome that starts at the top of the circle found on the layer above
# and ends with the top horizontal
# The first param here is the starting angle of the dome (essentially the tangent of the dome at the circle)
# 0 would be a full dome looking thing, pi/2 would basically be flat
arc_gen = ArcGenerator((math.pi/2)-0.05, circle_radius, layer_height)

# num circle segments per layer
circle_steps = 100
layers=[]
bottom_layers=[]
term = False
step_nums = 0

temp_set=False

initial_offset = None
while not term:
    term, R, offset = arc_gen.step()

    if term:
        break

   
    step_nums += 1
    if (initial_offset is None):
        initial_offset = offset
        
    offset = offset - initial_offset

    layer = layer_from_circle(R, circle_center, offset, start_angle, min_seconds_per_circle, extrude_mm_per_mm, extrude_temp if temp_set == False else None)

    # Set the extruder temp (For PLA) only on the first layer so it can be tuned
    if (temp_set == False):
        temp_set = True

    #layer.add_terminator()
    layers.append(layer)

    # Add another layer 3 rings back so we can leave room for the extruder
    # if (step_nums > 3):
    #     term, R2, offset2 = arc_gen.step_for_params(arc_gen.angle-(arc_gen.step_beta*2.5), arc_gen.sphere_radius+layer_height)
    #     offset2 = offset2 - initial_offset
    #     layer2 = layer_from_circle(R2, circle_center, offset2, start_angle, min_seconds_per_circle, extrude_mm_per_mm/2, None)
    #     layer2.add_terminator()
    #     layers.append(layer2)
    

ll_out = LayerList(start_layers+layers+end_layers)


with open(file+".out.gcode", 'w') as f:
    f.write(ll_out.render())