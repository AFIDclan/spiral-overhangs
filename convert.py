from LayerList import *
from Helpers import *
import numpy as np
import math
import copy

file="Test print"

ll = LayerList.FromFile(file+".gcode")

start_layers = ll.layers[0:10]
end_layers = ll.layers[-1:]

# Mostly working -----
# extrude_rate = 0.033
# layer_height = 0.3

extrude_mm_per_mm = 0.06281503928279897
layer_height = 0.4
extrude_temp = 198
min_seconds_per_circle = 15


ret, circle_center, circle_radius, start_angle = fit_circle(start_layers[-1])


arc_gen = ArcGenerator((math.pi/2)-0.05, circle_radius, layer_height)

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

    seg_len = (R*2*math.pi)/circle_steps

    extrude_per_segment = extrude_mm_per_mm*seg_len

    step_nums += 1
    if (initial_offset is None):
        initial_offset = offset
        
    offset = offset - initial_offset

    
    #Create a circle of positions around the center
    layer = Layer()
    layer.lines = [] # Needed to clear the lines from the previous layer. NO idea why we need this.

    # Set the extruder temp (For PLA) only on the first layer so it can be tuned
    if (temp_set == False):
        temp_set = True
        temp = ExtruderTemp()
        temp.s = extrude_temp
        layer.add(temp)

    
    feedrate = R*2*math.pi/min_seconds_per_circle
    feedrate = min(feedrate, 15)
    feedrate = max(feedrate, 5)

    feedrate = 5
    pos=None
 
    for i in range(circle_steps):
        ang = i/circle_steps*2*np.pi
        ang = ang + start_angle
        pos = Position()
        pos.x = circle_center[0] + R*np.cos(ang)
        pos.y = circle_center[1] + R*np.sin(ang)
        pos.z = circle_center[2] + offset
        pos.e = extrude_per_segment

        # Convert mm/s to mm/min
        pos.f = feedrate * 60
        

        layer.add(pos)

    layer.add_terminator()
    layers.append(layer)
    
    bottom_layers.append(layer)

    if (len(bottom_layers) > 1):
        layer = copy.deepcopy(bottom_layers[-2])
        
        # Loop through the positions and bump the z up by the layer height
        for pos in layer.get_positions():
            pos.z += layer_height

        layers.append(layer)

    


ll_out = LayerList(start_layers+layers+end_layers)


with open(file+".out.gcode", 'w') as f:
    f.write(ll_out.render())