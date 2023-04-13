# Import the necessary libraries
import re
import numpy as np
from scipy.optimize import minimize

max_gap = 0.15


def add_position(layer, pos, extrude=0.03231):
    layer.append('G1 Z{} X{} Y{} E{}'.format(pos[2], pos[0], pos[1], extrude))


def circlify(lines):

    positions = []

    for line in lines:
        # Check if the line contains an X, Y, or Z coordinate
        if line.startswith('G1') and ('X' in line and 'Y' in line and 'Z' in line):

            # Extract the X, Y, and Z coordinates from the line
            x = float(line.split('X')[-1].split()[0])
            y = float(line.split('Y')[-1].split()[0])
            z = float(line.split('Z')[-1].split()[0])
            positions.append([x, y, z])

    if len(positions) < 10:
        return False, None, None

    # Convert positions to a numpy array
    positions = np.array(positions)

    # Calculate the center of the points
    center = np.mean(positions, axis=0)

    # Define the objective function for optimization
    def objective(params):
        xc, yc, zc, r = params
        return np.sum((positions[:, 0] - xc) ** 2 + (positions[:, 1] - yc) ** 2 + (positions[:, 2] - zc) ** 2 - r ** 2) ** 2

    # Set the initial guess for the optimization
    initial_guess = np.concatenate([center, [1]])

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
    print(score)
    return True, np.array([xc, yc, zc]), r


# Define the function to read in the gcode file and split it by layer
def split_gcode_by_layer(gcode_file):
    # Open the gcode file and read in the lines
    with open(gcode_file, 'r') as f:
        lines = f.readlines()

    # Initialize the variables
    layer_number = 0
    layer_lines = []
    layers = []

    # Loop through each line in the file
    for line in lines:
        # Check if the line is a layer change command
        if line.startswith(';LAYER_CHANGE'):
            # If it is, add the current layer's lines to the layers list and start a new layer
            if layer_lines:
                layers.append(layer_lines)
                layer_lines = []
                layer_lines.append(line.strip())
            layer_number += 1
        # If the line is not a layer change command, add it to the current layer's lines
        else:
            layer_lines.append(line.strip())

    # Add the last layer's lines to the layers list
    if layer_lines:
        layers.append(layer_lines)

    return layers


def write_gcode_file(filename, layers):
    with open(filename, 'w') as f:
        for layer in layers:
            for line in layer:
                f.write(line + '\n')


# Call the function with your gcode file as the argument
layers = split_gcode_by_layer('dome.gcode')

# Print the number of layers and the commands in each layer
print(f"Number of layers: {len(layers)}")
for i, layer in enumerate(layers):
    if (i>0):
        last_circle, last_center, last_radius = circlify(layers[i-1])
        this_circle, this_center, this_radius = circlify(layers[i])

        if last_circle and this_circle:
            # If the circles are such that the lines of the circles aren't touching:
            if abs(last_radius-this_radius) > max_gap:
                # Create however many circles it takes to fill the space between them
                num_circles = int(np.ceil(abs(last_radius-this_radius) / max_gap))
                print("Adding: " + str(num_circles))
                for j in range(num_circles):
                    # Calculate the center of the new circle
                    alpha = (j + 1) / (num_circles + 1)
                    center = alpha * last_center + (1 - alpha) * this_center

                    # Calculate the radius of the new circle
                    radius = (j + 1) / (num_circles + 1) * last_radius + (1 - alpha) * this_radius

                    # Loop through the circles and add positions around the circles
                    for theta in np.linspace(0, 2*np.pi, num=50):
                        x = center[0] + radius * np.cos(theta)
                        y = center[1] + radius * np.sin(theta)
                        z = center[2]
                        add_position(layers[i-1], [x, y, z])

write_gcode_file("out.gcode", layers)