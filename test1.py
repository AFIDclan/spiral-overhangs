from LayerList import Layer
from LayerList import Position
from LayerList import LayerList
import numpy as np
ll = LayerList.FromFile("dome.gcode")

start_layers = ll.layers[0:10]
end_layers = ll.layers[-1:]

layers=[]

#Create a circle of positions around the center
for i in range(20):
    pos = Position()
    pos.x = 50 + 25*np.cos(i/20*2*np.pi)
    pos.y = 50 + 25*np.sin(i/20*2*np.pi)
    pos.z = 0.1
    layers.append(pos)

ll_out = LayerList(start_layers+layers+end_layers)


with open("out2.gcode", 'w') as f:
    f.write(ll_out.render())