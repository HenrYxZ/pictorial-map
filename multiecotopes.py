import json
import numpy as np
import os.path
from PIL import Image

# Local modules
import dithering
from utils import Point
import utils


DENSITY_FILENAME = "density_map.png"
PLACEMENT_MAP_FILENAME = "placement_map.jpg"
HEIGHT_MAP_FILENAME = "height_map.png"
SURFACE_FILENAME = "surface.json"
PLACEMENT_FILENAME = "placement.json"
ECOTOPES_FILENAME = "ecotopes.json"
MAX_COLOR = 255
MAX_QUALITY = 95
ROUND_DECIMALS = 3
# Indent 2 spaces in JSON files
JSON_INDENT = 2
# Allow only -+10% offset in position
MAX_POS_OFFSET = 0.2
# Default maximum height for the ground
DEFAULT_MAX_HEIGHT = 64
# Allowed rotations
ROTATIONS = [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]
# Map size will be 200mt^2
MAP_SIZE = 200
# Density maps will be 40x40 pixels
DENSITY_MAP_SIZE = 40
# Each pixel will represent 5 mt square
PIXEL_SIZE = 8
# Each pixel in height map will represent 1 mt^2
HEIGHT_MAP_PIXEL_SIZE = 1
rng = np.random.default_rng()
cities = ["Shechem", "Jerusalem"]
chosen_option = "shechem"


def create_ground(
        height_map,
        max_height=DEFAULT_MAX_HEIGHT,
        pixel_size=HEIGHT_MAP_PIXEL_SIZE
):
    """
    Gets a height_map that is a 2D array of floats from 0 to 1 and creates a
    JSON with two triangles for each pixel
    Args:
        height_map(2darray): Map where each pixel represents a height
        max_height(float): Maximum height for a vertex
        pixel_size(float): Length of a side of a pixel in the height map
    Returns:
        dict: An array of triangles
    """
    print("Creating surface from height map...")
    ground = []
    h, w = height_map.shape
    # Iterate through pixels creating two triangles on each
    for j in range(h):
        for i in range(w):
            x0 = (i - w / 2) * pixel_size
            x1 = x0 + pixel_size
            z0 = (j - h / 2) * pixel_size
            z1 = z0 + pixel_size
            """
                |v2 |v1
             ---|---|---           tr1 = v0, v1, v2
                |v0 |v3
             ---|---|---           tr2 = v0, v3, v1
                |   |  
            """
            y0 = height_map[j][i]
            if i == w - 1 or j == 0:
                y1 = y0
                y2 = y0
                y3 = y0
            else:
                y1 = (height_map[j - 1][i + 1]) * max_height
                y2 = (height_map[j - 1][i]) * max_height
                y3 = (height_map[j][i + 1]) * max_height
            # Create vertices of two triangles
            v0 = Point(x0, y0, z1)
            v1 = Point(x1, y1, z0)
            v2 = Point(x0, y2, z0)
            v3 = Point(x1, y3, z1)
            ground.append({
                'v0': v0.to_dict(),
                'v1': v1.to_dict(),
                'v2': v2.to_dict()
            })
            ground.append({
                'v0': v0.to_dict(),
                'v1': v3.to_dict(),
                'v2': v1.to_dict()
            })
    return ground


def discretize_density(density_map, ecotope_name):
    # Discretize Density Map
    opt = input(
        "Enter an option:\n"
        "[1] for Floyd-Steinberg Error diffusion \n"
        "[2] for Ordered Dithering\n"
        "[0] to quit\n"
    )
    if opt == '0':
        quit()
    timer = utils.Timer()
    timer.start()
    # Discretize with Dithering
    if opt == '1':
        print("Using Floyd-Steinberg Error Diffusion Dithering...")
        output = dithering.floyd_steinberg_dithering(density_map)
    else:
        print("Using Ordered Dithering...")
        output = dithering.ordered_dithering(density_map)
    # Save as Placement Map
    output_img = Image.fromarray(output)
    placement_map_path = (
        f"assets/{chosen_option}/{ecotope_name}_{PLACEMENT_MAP_FILENAME}"
    )
    output_img.save(placement_map_path, quality=MAX_QUALITY)
    print(f"Image saved in {placement_map_path}")
    timer.stop()
    print(f"Total time spent: {timer}")
    return output


def place_asset(asset, i, j, w, h, footprint):
    if 'allowOffset' in asset:
        position_offset = (-0.5 + rng.random(2)) * asset['allowOffset']
    else:
        position_offset = np.zeros(2)
    # rotation = rng.choice(ROTATIONS)
    if 'allowRotation' in asset:
        rotation = rng.random() * asset['allowRotation']
    else:
        rotation = 0
    if 'allowScale' in asset:
        scale_offset = rng.random(3) * asset['allowScale']
    else:
        scale_offset = np.zeros(3)
    x = (i - w / 2 + 0.5 + position_offset[0]) * footprint
    y = 0
    z = (j - h / 2 + 0.5 + position_offset[1]) * footprint
    pos = Point(x, y, z)
    scale = np.ones(3) - scale_offset
    s = Point(scale[0], scale[1], scale[2])
    placement_dict = {
        'assetId': asset['assetId'],
        'position': pos.to_dict(),
        'rotation': float(np.round(rotation, ROUND_DECIMALS)),
        'scale': s.to_dict()
    }
    return placement_dict


def procedurally_place(placement_map, ecotope):
    ratio = int(PIXEL_SIZE // ecotope['footprint'])
    if ratio > 1:
        # Divide the pixels so that multiple assets can be placed
        placement_map = utils.resize(placement_map, ratio)
        footprint = PIXEL_SIZE / ratio
    else:
        footprint = PIXEL_SIZE
    h, w = placement_map.shape
    # Iterate placing assets
    placement_json = []
    # Iterate on pixels
    for j in range(h):
        for i in range(w):
            if placement_map[j][i]:
                p = rng.random()
                accumulated_prob = 0
                for asset in ecotope['data']:
                    accumulated_prob += asset['probability']
                    if p <= accumulated_prob:
                        placement_dict = place_asset(
                            asset, i, j, w, h, footprint
                        )
                        placement_json.append(placement_dict)
                        break
    return placement_json


def main():
    global chosen_option
    option = int(input(utils.menu_str(cities))) - 1
    chosen_option = cities[option].lower()

    # Load height map
    height_map_path = f"assets/{chosen_option}/{HEIGHT_MAP_FILENAME}"
    if os.path.isfile(height_map_path):
        img = Image.open(height_map_path)
        grayscale = img.convert('L')
        height_map = np.array(grayscale, dtype=float) / MAX_COLOR
        # Create triangles for height map
        height_map_json = create_ground(height_map)
        # Store triangles into surface JSON
        surface_path = f"assets/{chosen_option}/{SURFACE_FILENAME}"
        with open(surface_path, 'w') as f:
            json.dump(height_map_json, f, indent=JSON_INDENT)
        print(f"Finished writing surface json file in {surface_path}")

    # Load ecotopes
    ecotopes_path = f"assets/{chosen_option}/{ECOTOPES_FILENAME}"
    with open(ecotopes_path, 'r') as f:
        ecotopes = json.load(f)
    # Iterate on ecotopes
    placement_json = []
    ecotopes = sorted(ecotopes, key=lambda e: e['priority'])
    combined_density_map = np.zeros([DENSITY_MAP_SIZE, DENSITY_MAP_SIZE])
    ones = np.ones([DENSITY_MAP_SIZE, DENSITY_MAP_SIZE])
    for ecotope in ecotopes:
        ecotope_name = ecotope['name']
        density_map_file = (
            f"assets/{chosen_option}/{ecotope_name}_density_map.png"
        )
        # Open Density Map
        img = Image.open(density_map_file)
        grayscale = img.convert('L')
        density_map = np.array(grayscale, dtype=float) / MAX_COLOR
        density_map = density_map * (ones - combined_density_map)
        combined_density_map = density_map
        # Discretize
        placement_map = discretize_density(density_map, ecotope_name)
        # Procedurally place
        placement_json += procedurally_place(placement_map, ecotope)
    # Save placement array in JSON
    placement_path = f"assets/{chosen_option}/{PLACEMENT_FILENAME}"
    with open(placement_path, 'w') as f:
        json.dump(placement_json, f, indent=JSON_INDENT)
    print(f"Finished writing placement json file in {placement_path}")


if __name__ == '__main__':
    main()
