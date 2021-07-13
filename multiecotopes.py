import json
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
# Textures
GROUND_TEXTURE = "ground.png"    # colors for the ground triangles
SURFACE_TEXTURE = "surface.png"  # colors for surface triangle, counting roads

MAX_COLOR = 255
MAX_QUALITY = 95
ROUND_DECIMALS = 3
# Indent 2 spaces in JSON files
JSON_INDENT = 2
# Allow only -+10% offset in position
MAX_POS_OFFSET = 0.2
# Default maximum height for the ground
DEFAULT_MAX_HEIGHT = 32
# Allowed rotations
ROTATIONS = [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]
# Map size will be 200mt^2
MAP_SIZE = 200
# Density maps will be 40x40 pixels
DENSITY_MAP_SIZE = 40
# Each pixel will represent 8 mt square
PIXEL_SIZE = 8
# Each pixel in height map will represent 1 mt^2
HEIGHT_MAP_PIXEL_SIZE = 1
rng = np.random.default_rng()
cities = [
    {
        "name": "Shechem",
        "colors": {"roads": [105, 96, 70], "ground": [161, 153, 95]}
    },
    {
        "name": "Jerusalem",
        "colors": {"roads": [89, 70, 75], "ground": [161, 153, 148]}
    }
]
chosen_option = "shechem"


def get_ground_texture(ground_texture_filename, h, w):
    if os.path.exists(ground_texture_filename):
        ground_img = Image.open(ground_texture_filename)
        resized_ground_img = ground_img.resize([h, w])
        ground_texture = np.asarray(resized_ground_img)
        return ground_texture
    else:
        return None


def get_ground_color_at(ground_texture, i, j, option):
    if ground_texture is not None:
        ground_color = ground_texture[j][i]
    else:
        ground_color = np.array(cities[option].get('colors').get('ground'))
    return ground_color


def paint_surface(road_map, option):
    """
    Create a texture for the surface (road + ground)
    Args:
        road_map(Image): Map where each pixel represents the density of road
        option(int): Option of the chosen city
    Returns:
        2darray: Texture with the colors for the surface in uint8
    """
    road_map_arr = np.asarray(road_map) / MAX_COLOR
    h, w = road_map_arr.shape
    surface_texture = np.zeros([h, w, COLOR_CHANNELS], dtype=np.uint8)
    ground_texture_filename = f"assets/{chosen_option}/{GROUND_TEXTURE}"
    road_color = np.array(cities[option].get('colors').get('roads'))
    # Each pixel color will take the color for the road in road pixels and the
    # color for the ground in the rest
    ground_texture = get_ground_texture(ground_texture_filename, h, w)
    for j in range(h):
        for i in range(w):
            # Ground texture will need to match shape of road map
            ground_color = get_ground_color_at(ground_texture, i, j, option)
            road_weight = road_map_arr[j][i]
            surface_texture[j][i] = (
                road_weight * road_color + (1 - road_weight) * ground_color
            )
    return surface_texture


def create_surface(
    height_map,
    max_height=DEFAULT_MAX_HEIGHT,
    pixel_size=HEIGHT_MAP_PIXEL_SIZE
):
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


def get_height(x, z, height_map, max_height):
    """
    Get the height for an asset to be placed in the map. It uses image
    interpolation in the height map.
    Args:
        x: position of the asset in the x axis
        z: position of the asset in the x axis
        height_map: the map with height information as a float 2D array
        max_height: the maximum height in the scene

    Returns:
        float: height for the given position
    """
    # Add 0.5 because the origin is moved to the middle of the
    h, w = height_map.shape
    u = x / (w * HEIGHT_MAP_PIXEL_SIZE) + 0.5
    v = -z / (h * HEIGHT_MAP_PIXEL_SIZE) + 0.5
    normalized_height = utils.blerp(height_map, u, v)
    if normalized_height > 1:
        print("mama mia!")
    height = normalized_height * max_height
    return height


def get_orientation(x, z, orient_map):
    h, w, _ = orient_map.shape
    u = x / (w * HEIGHT_MAP_PIXEL_SIZE) + 0.5
    v = -z / (h * HEIGHT_MAP_PIXEL_SIZE) + 0.5
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


def place_asset(
    asset, i, j, w, h, footprint, height_map, max_height, orient_map=None
):
    # Position
    if 'allowOffset' in asset:
        position_offset = (-0.5 + rng.random(2)) * asset['allowOffset']
    else:
        position_offset = np.zeros(2)
    x = (i - w / 2 + 0.5 + position_offset[0]) * footprint
    z = (j - h / 2 + 0.5 + position_offset[1]) * footprint
    y = get_height(x, z, height_map, max_height)
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
        rotation = rng.random() * asset['allowRotation']
    else:
        if orient_map is not None:
            rotation = get_orientation(x, z, orient_map)
        else:
            rotation = 0
    placement_dict = {
        'assetId': asset['assetId'],
        'position': pos.to_dict(),
        'rotation': float(np.round(rotation, ROUND_DECIMALS)),
        'scale': s.to_dict()
    }
    return placement_dict


def procedurally_place(
    placement_map, ecotope, height_map, max_height, orient_map=None
):
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
                            normalized_height_map, max_height, orient_map
                        )
                        placement_json.append(placement_dict)
                        break
    return placement_json


# noinspection PyUnreachableCode
def main():
    global chosen_option
    # option = int(input(utils.menu_str(cities))) - 1
    option = 0
    chosen_option = cities[option]["name"].lower()

    timer = utils.Timer()
    timer.start()
    # Load road map
    road_map_path = f"assets/{chosen_option}/{ROAD_MAP_FILENAME}"
    new_size = (DENSITY_MAP_SIZE, DENSITY_MAP_SIZE)
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
        orient_map = roads.create_orient_map(dist_map)
        orient_map_img = Image.fromarray(orient_map)
        orient_map_img.save(
            f'{DEBUG_DIR}/{chosen_option}/{ORIENT_MAP_FILENAME}'
        )
    # Load height map
    height_map_path = f"assets/{chosen_option}/{HEIGHT_MAP_FILENAME}"
    if not os.path.isfile(height_map_path):
        print(f"Height map {height_map_path} not found")
    img = Image.open(height_map_path)
    height_map_img = img.convert('L')
    height_map = np.array(height_map_img, dtype=np.uint8)
    max_height = DEFAULT_MAX_HEIGHT
    # Load ecotopes
    ecotopes_path = f"assets/{chosen_option}/{ECOTOPES_FILENAME}"
    with open(ecotopes_path, 'r') as f:
        ecotopes = json.load(f)
    # Iterate on ecotopes
    placement_json = []
    ecotopes = sorted(ecotopes, key=lambda e: e['priority'])
    combined_density_map = np.zeros([DENSITY_MAP_SIZE, DENSITY_MAP_SIZE])
    ones = np.ones([DENSITY_MAP_SIZE, DENSITY_MAP_SIZE])
    # Combine road maps so density maps don't use that part
    if road_map is not None:
        resized_road_map = road_map.resize(new_size)
        road_map_arr = np.asarray(resized_road_map, dtype=float) / MAX_COLOR
        combined_density_map = road_map_arr
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
            placement_map, ecotope, height_map, max_height, orient_map
        )
    # Create the texture for the surface
    surface_texture = paint_surface(road_map, option)
    surface_tex_img = Image.fromarray(surface_texture)
    surface_tex_path = f"assets/{chosen_option}/{SURFACE_TEXTURE}"
    surface_tex_img.save(surface_tex_path)
    print(f"Image saved in {surface_tex_path}")
    # Create surface JSON from height map
    surface_json = create_surface(height_map)
    # Store triangles into surface JSON
    surface_path = f"assets/{chosen_option}/{SURFACE_FILENAME}"
    with open(surface_path, 'w') as f:
        json.dump(surface_json, f, indent=JSON_INDENT)
    print(f"Finished writing surface json file in {surface_path}")
    # Save placement array in JSON
    placement_path = f"assets/{chosen_option}/{PLACEMENT_FILENAME}"
    with open(placement_path, 'w') as f:
        json.dump(placement_json, f, indent=JSON_INDENT)
    print(f"Finished writing placement json file in {placement_path}")
    timer.stop()
    print(f"Elapsed time in the program was {timer}")


if __name__ == '__main__':
    main()
