import numpy as np
from scipy.optimize import minimize
import math
from LayerList import *

def fit_circle(layer):

    positions = []

    for pos in layer.get_positions():
        if (pos.x is None or pos.y is None or pos.z is None):
            continue
        positions.append([pos.x, pos.y, pos.z])

    # Convert positions to a numpy array
    positions = np.array(positions[2:])
    # Calculate the center of the points
    center = np.mean(positions, axis=0)

     # Define the objective function for optimization
    def objective(params):
        xc, yc, zc, r = params
        return np.sum((positions[:, 0] - xc) ** 2 + (positions[:, 1] - yc) ** 2 + (positions[:, 2] - zc) ** 2 - r ** 2) ** 2

    # Set the initial guess for the optimization
    initial_guess = np.concatenate([center, [100]])

    # Perform the optimization
    result = minimize(objective, initial_guess, method='L-BFGS-B')

    # Check if the optimization succeeded
    if not result.success:
        return False, None, None

    # Extract the optimized parameters
    xc, yc, zc, r = result.x

    # Calculate the score for the circle fitting
    distances = np.sqrt((positions[:, 0] - xc) ** 2 + (positions[:, 1] - yc) ** 2 + (positions[:, 2] - zc) ** 2)
    score = np.sum((distances - r) ** 2)

    start_angle = np.arctan2(positions[-1][1]-yc, positions[-1][0]-xc)

    return True, np.array([xc, yc, zc]), r, start_angle

def layer_from_circle(
    R, 
    circle_center, 
    offset, 
    start_angle,
    min_seconds_per_circle, 
    extrude_mm_per_mm):

    circle_steps = 100

    seg_len = (R*2*math.pi)/circle_steps

    extrude_per_segment = extrude_mm_per_mm*seg_len


        #Create a circle of positions around the center
    layer = Layer()
    layer.lines = [] # Needed to clear the lines from the previous layer. NO idea why we need this.

    
    feedrate = R*2*math.pi/min_seconds_per_circle
    feedrate = min(feedrate, 12)
    feedrate = max(feedrate, 5)

    # feedrate = 5
    pos=None
 
    for i in range(circle_steps+1):
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

    layer.get_positions()[0].e = 0
    layer.add_terminator()

    return layer


class ArcGenerator:
    def __init__(self, start_ang, start_radius, step_length):
        self.sphere_radius = start_radius/math.cos(start_ang)
        self.sphere_radius = min(self.sphere_radius, 4000)
        self.step_length = step_length
        self.step_beta = 2*math.asin(step_length/(2*self.sphere_radius))

        self.angle = start_ang

    def step(self):
        
        if self.angle > math.pi/2:
            return True, None, None

        res = self.step_for_params(self.angle, self.sphere_radius)

        self.angle += self.step_beta

        return res

    def step_for_params(self, angle, sphere_radius):
        radius = sphere_radius*math.cos(angle)
        height = sphere_radius*math.sin(angle)

        return False, radius, height
