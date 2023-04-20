from LayerList import *
from Helpers import *
import numpy as np
import math
import copy

ll = LayerList.FromFile("dome2.gcode")

start_layers = ll.layers[0:10]
end_layers = ll.layers[-1:]

# Mostly working -----
# extrude_rate = 0.033
# layer_height = 0.3

extrude_mm_per_mm = 0.06281503928279897
layer_height = 0.4

min_seconds_per_circle = 15


ret, circle_center, circle_radius, start_angle = fit_circle(start_layers[-1])


arc_gen = ArcGenerator((math.pi/2)-0.1, circle_radius, layer_height)

circle_steps = 100
layers=[]
term = False
step_nums = 0

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

    temp = ExtruderTemp()
    temp.s = 185

    #bed_temp = BedTemp()
    #bed_temp.s = 40

    layer.add(temp) # Set the extruder temp (For PLA)
    #layer.add(bed_temp) # Set the extruder temp (For PLA)
    
    
    # feedrate = R*2*math.pi/min_seconds_per_circle
    # feedrate = min(feedrate, 4)
    # feedrate = max(feedrate, 1)

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


ll_out = LayerList(start_layers+layers+end_layers)


with open("out3.gcode", 'w') as f:
    f.write(ll_out.render())