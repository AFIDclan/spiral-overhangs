import numpy as np
from scipy.optimize import minimize
import math

def fit_circle(layer):

    positions = []

    for pos in layer.get_positions():
        if (pos.x is None or pos.y is None or pos.z is None):
            continue
        positions.append([pos.x, pos.y, pos.z])

    # Convert positions to a numpy array
    positions = np.array(positions[4:])
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


class ArcGenerator:
    def __init__(self, start_ang, start_radius, step_length):
        self.sphere_radius = start_radius/math.cos(start_ang)
        self.sphere_radius = min(self.sphere_radius, 4000)
        self.step_length = step_length
        self.step_beta = 2*math.asin(step_length/(2*self.sphere_radius))

        self.angle = start_ang

    def step(self):
        self.angle += self.step_beta
        if self.angle > math.pi/2:
            return True, None, None
        
        radius = self.sphere_radius*math.cos(self.angle)
        height = self.sphere_radius*math.sin(self.angle)

        return False, radius, height
