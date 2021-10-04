import json
import math

import numpy as np
import os.path
from PIL import Image

# Local modules
import dithering
import roads
from utils import COLOR_CHANNELS
from utils import Point
import utils


# Directories
DEBUG_DIR = "debug"
ASSETS_DIR = "assets"
# Maps
DENSITY_FILENAME = "density_map.png"
PLACEMENT_MAP_FILENAME = "placement_map.jpg"
HEIGHT_MAP_FILENAME = "height_map.png"
ROAD_MAP_FILENAME = "road_map.png"
DIST_MAP_FILENAME = "dist_map.png"
ORIENT_MAP_FILENAME = "orient_map.png"
# JSONs
SURFACE_FILENAME = "surface.json"
PLACEMENT_FILENAME = "placement.json"
ECOTOPES_FILENAME = "ecotopes.json"
CONFIG_FILENAME = "config.json"
# Textures
GROUND_TEXTURE = "ground.png"    # colors for the ground triangles
SURFACE_TEXTURE = "surface.png"  # colors for surface triangle, counting roads

MAX_COLOR = 255
MAX_QUALITY = 95
ROUND_DECIMALS = 3
# Indent 2 spaces in JSON files
JSON_INDENT = 2
# Define a key value rotation for the 3 axis
FULL_ROTATION = "full"
rng = np.random.default_rng()
cities = ["Jerusalem", "Shechem", "San-fran"]
chosen_option = "shechem"
config = {}


def paint_surface(road_map, road_color, ground_texture):
    """
    Create a texture for the surface (road + ground)
    Args:
        road_map(Image): Map where each pixel represents the density of road
        road_color(ndarray): RGB color for the road
        ground_texture(ndarray): RGB texture for the ground
    Returns:
        2darray: Texture with the colors for the surface in uint8
    """
    road_map_arr = np.asarray(road_map) / MAX_COLOR
    h, w = road_map_arr.shape
    surface_texture = np.zeros([h, w, COLOR_CHANNELS], dtype=np.uint8)
    for j in range(h):
        for i in range(w):
            # Ground texture will need to match shape of road map
            ground_color = ground_texture[j][i]
            road_weight = road_map_arr[j][i]
            surface_texture[j][i] = (
                road_weight * road_color + (1 - road_weight) * ground_color
            )
    return surface_texture


def create_surface(height_map, max_height, pixel_size):
    """
    Create a JSON with the necessary information to build the surface of a map
    Args:
        height_map(2darray): Map where each pixel represents a height (uint8)
        max_height(float): Maximum height for all vertices
        pixel_size(float): Length of a side of a pixel in the height map
    Returns:
        dict: A JSON with the necessary info for creating the surface of the map
    """
    height, width = height_map.shape
    surface_object = {
        "heightMap": height_map.tolist(),
        "maxHeight": max_height,
        "pixelSize": pixel_size,
        "height": height,
        "width": width
    }
    return surface_object


def discretize_density(density_map, ecotope_name):
    # Discretize Density Map
    # opt = input(
    #     "Enter an option:\n"
    #     "[1] for Floyd-Steinberg Error diffusion \n"
    #     "[2] for Ordered Dithering\n"
    #     "[0] to quit\n"
    # )
    opt = '1'
    if opt == '0':
        quit()
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
    return output


def get_height(x, z, height_map):
    """
    Get the height for an asset to be placed in the map. It uses image
    interpolation in the height map.
    Args:
        x: position of the asset in the x axis
        z: position of the asset in the x axis
        height_map: the map with height information as a float 2D array

    Returns:
        float: height for the given position
    """
    # Add 0.5 because the origin is moved to the middle of the
    h, w = height_map.shape
    max_height = config['maxHeight']
    height_map_pixel_size = config['heightMapPixelSize']
    u = x / (w * height_map_pixel_size) + 0.5
    v = -z / (h * height_map_pixel_size) + 0.5
    normalized_height = utils.blerp(height_map, u, v)
    height = normalized_height * max_height
    return height


def get_orientation(x, z, orient_map):
    h, w, _ = orient_map.shape
    height_map_pixel_size = config['heightMapPixelSize']
    u = x / (w * height_map_pixel_size) + 0.5
    v = -z / (h * height_map_pixel_size) + 0.5
    i = int(round(u * w))
    j = int(round(v * h))
    orient_pixel = orient_map[j][i]
    dx = (orient_pixel[0] - MAX_COLOR / 2) * 2
    dy = (orient_pixel[1] - MAX_COLOR / 2) * 2
    orient_unit_vector = utils.normalize([dx, dy])
    # Get the angle of rotation in the Z axis
    rotation = np.arccos(orient_unit_vector[0])
    if orient_pixel[1] < 0:
        rotation *= -1
    return rotation


def fix_rotation(rotation, asset_id):
    if asset_id in [1, 7, 4, 8]:
        return rotation + math.pi / 2
    elif asset_id in [6, 10]:
        return rotation - math.pi / 2
    else:
        return rotation


def place_asset(asset, i, j, w, h, footprint, height_map, orient_map=None):
    # Position
    if 'allowOffset' in asset:
        position_offset = (-0.5 + rng.random(2)) * asset['allowOffset']
    else:
        position_offset = np.zeros(2)
    x = (i - w / 2 + 0.5 + position_offset[0]) * footprint
    z = (j - h / 2 + 0.5 + position_offset[1]) * footprint
    y = get_height(x, z, height_map)
    pos = Point(x, y, z)
    # Scale
    if 'allowScale' in asset:
        scale_offset = (rng.random() - 0.5) * asset['allowScale'] * np.ones(3)
    else:
        scale_offset = np.zeros(3)
    scale = np.ones(3) - scale_offset
    s = Point(scale[0], scale[1], scale[2])
    # Rotation
    # rotation = rng.choice(ROTATIONS)
    if 'allowRotation' in asset:
        if asset['allowRotation'] == FULL_ROTATION:
            rotation = FULL_ROTATION
        else:
            rotation = rng.random() * asset['allowRotation']
    else:
        if orient_map is not None:
            rotation = get_orientation(x, z, orient_map)
        else:
            rotation = 0
    # REMOVE THIS LINE (IT'S ONLY FOR THIS ASSETS)
    if rotation != FULL_ROTATION:
        rotation = fix_rotation(rotation, int(asset['assetId']))
        rotation = float(np.round(rotation, ROUND_DECIMALS))
    placement_dict = {
        'assetId': asset['assetId'],
        'position': pos.to_dict(),
        'rotation': rotation,
        'scale': s.to_dict()
    }
    return placement_dict


def procedurally_place(placement_map, ecotope, height_map, orient_map=None):
    pixel_size = config['densityMapPixelSize']
    ratio = int(pixel_size // ecotope['footprint'])
    if ratio > 1:
        # Divide the pixels so that multiple assets can be placed
        placement_map = utils.resize(placement_map, ratio)
        footprint = pixel_size / ratio
    else:
        footprint = pixel_size
    h, w = placement_map.shape
    # Iterate placing assets
    placement_json = []
    # Create a height map array with float values between 0 and 1
    normalized_height_map = np.array(height_map, dtype=float) / MAX_COLOR
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
                            asset, i, j, w, h, footprint,
                            normalized_height_map, orient_map
                        )
                        placement_json.append(placement_dict)
                        break
    return placement_json


def main():
    global chosen_option
    global config
    option = int(input(utils.menu_str(cities))) - 1
    # option = 0
    chosen_option = cities[option].lower()

    timer = utils.Timer()
    timer.start()
    # Load map config
    config_path = f"assets/{chosen_option}/{CONFIG_FILENAME}"
    with open(config_path, 'r') as f:
        config = json.load(f)
    height_map_pixel_size = config['heightMapPixelSize']
    max_height = config['maxHeight']
    density_map_pixel_size = config['densityMapPixelSize']
    road_color = np.array(config['roadColor'])
    # Load height map
    height_map_path = f"assets/{chosen_option}/{HEIGHT_MAP_FILENAME}"
    if not os.path.isfile(height_map_path):
        print(f"Height map {height_map_path} not found")
    img = Image.open(height_map_path)
    height_map_img = img.convert('L')
    height_map = np.array(height_map_img, dtype=np.uint8)

    # Load road map
    road_map_path = f"assets/{chosen_option}/{ROAD_MAP_FILENAME}"

    density_map_size = int(
        math.ceil(
            (height_map.shape[0] * height_map_pixel_size) /
            density_map_pixel_size
        )
    )
    new_size = (density_map_size, density_map_size)
    if not os.path.isfile(road_map_path):
        road_map = None
        orient_map = None
    else:
        utils.exist_or_create(f'{DEBUG_DIR}')
        utils.exist_or_create(f'{DEBUG_DIR}/{chosen_option}')
        road_map = Image.open(road_map_path).convert('L')
        dist_map = roads.create_dist_map(road_map)
        dist_map_img = Image.fromarray(dist_map)
        dist_map_img.save(f'{DEBUG_DIR}/{chosen_option}/{DIST_MAP_FILENAME}')
        float_dist_map = np.array(dist_map, dtype=float)
        orient_map = roads.create_orient_map(float_dist_map, chosen_option)
        orient_map_img = Image.fromarray(orient_map)
        orient_map_img.save(
            f'{DEBUG_DIR}/{chosen_option}/{ORIENT_MAP_FILENAME}'
        )
    # Load ecotopes
    ecotopes_path = f"assets/{chosen_option}/{ECOTOPES_FILENAME}"
    with open(ecotopes_path, 'r') as f:
        ecotopes = json.load(f)
    # Iterate on ecotopes
    placement_json = []
    ecotopes = sorted(ecotopes, key=lambda e: e['priority'])
    combined_density_map = np.zeros([density_map_size, density_map_size])
    ones = np.ones([density_map_size, density_map_size])
    # Combine road maps so density maps don't use that part
    if road_map is not None:
        resized_road_map = road_map.resize(new_size)
        resized_road_map = np.array(resized_road_map, dtype=np.uint8)
        # high pass the road map
        resized_road_map = roads.high_pass(resized_road_map, MAX_COLOR)
        combined_density_map = (
            np.asarray(resized_road_map, dtype=float) / MAX_COLOR
        )
    # Combine ecotopes iterating them by hierarchy level
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
        # Retain the densities of the previous ecotopes to not place elements
        # over each other
        combined_density_map = np.maximum(density_map, combined_density_map)
        # Discretize
        placement_map = discretize_density(density_map, ecotope_name)
        # Procedurally place
        placement_json += procedurally_place(
            placement_map, ecotope, height_map, orient_map
        )
    # Create the texture for the surface
    ground_img_path = f"assets/{chosen_option}/{GROUND_TEXTURE}"
    if os.path.isfile(ground_img_path):
        ground_img = Image.open(ground_img_path)
        ground_texture = np.asarray(ground_img)
        surface_texture = paint_surface(road_map, road_color, ground_texture)
        surface_tex_img = Image.fromarray(surface_texture)
        surface_tex_path = f"assets/{chosen_option}/{SURFACE_TEXTURE}"
        surface_tex_img.save(surface_tex_path)
        print(f"Image saved in {surface_tex_path}")
    # Create surface JSON from height map
    surface_json = create_surface(height_map, max_height, height_map_pixel_size)
    # Store triangles into surface JSON
    surface_path = f"assets/{chosen_option}/{SURFACE_FILENAME}"
    with open(surface_path, 'w') as f:
        json.dump(surface_json, f, indent=JSON_INDENT)
    print(f"Finished writing surface json file in {surface_path}")
    # LANDMARKS REMOVE THIS
    if chosen_option == 'jerusalem':
        x = 194 - 320 / 2
        z = 93 - 320 / 2
        normalized_height_map = np.array(height_map, dtype=float) / MAX_COLOR
        y = get_height(x, z, normalized_height_map)
        pos = Point(x, y, z)
        s = Point(1, 1, 1)
        placement_dict = {
            'assetId': 11,
            'position': pos.to_dict(),
            'rotation': 0,
            'scale': s.to_dict()
        }
        placement_json.append(placement_dict)
    if chosen_option == 'shechem':
        x = 243 - 320 / 2
        z = 153 - 320 / 2
        normalized_height_map = np.array(height_map, dtype=float) / MAX_COLOR
        y = get_height(x, z, normalized_height_map)
        pos = Point(x, y, z)
        s = Point(3, 3, 3)
        placement_dict = {
            'assetId': 12,
            'position': pos.to_dict(),
            'rotation': math.pi / 2,
            'scale': s.to_dict()
        }
        placement_json.append(placement_dict)
    # Save placement array in JSON
    placement_path = f"assets/{chosen_option}/{PLACEMENT_FILENAME}"
    with open(placement_path, 'w') as f:
        json.dump(placement_json, f, indent=JSON_INDENT)
    print(f"Finished writing placement json file in {placement_path}")
    timer.stop()
    print(f"Elapsed time in the program was {timer}")


if __name__ == '__main__':
    main()
