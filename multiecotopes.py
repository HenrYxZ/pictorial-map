import json
import numpy as np
from PIL import Image

# Local modules
import dithering
import utils


DENSITY_FILENAME = "density_map.png"
PLACEMENT_MAP_FILENAME = "placement_map.jpg"
PLACEMENT_FILENAME = "placement.json"
ECOTOPES_FILENAME = "ecotopes.json"
MAX_COLOR = 255
MAX_QUALITY = 95
# Indent 2 spaces in JSON files
JSON_INDENT = 2
# Allow only -+10% offset in position
MAX_POS_OFFSET = 0.2
# Only allow up to 10% scale
MAX_SCALE = 0.1
MAX_ROTATION = 2 * np.pi
# Allowed rotations
ROTATIONS = [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]
# Map size will be 200mt^2
MAP_SIZE = 200
# Density maps will be 40x40 pixels
DENSITY_MAP_SIZE = 40
# Each pixel will represent 5 mt square
pixel_size = 5
rng = np.random.default_rng()
cities = ["Shechem", "Jerusalem"]
chosen_option = "shechem"


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
    x = (i - w // 2 + 0.5 + position_offset[0]) * footprint
    y = 0
    z = (j - h // 2 + 0.5 + position_offset[1]) * footprint
    # rotation = rng.choice(ROTATIONS)
    if "allowRotation" in asset:
        rotation = rng.random() * MAX_ROTATION
    else:
        rotation = 0
    scale_offset = rng.random() * MAX_SCALE
    scale = 1 - scale_offset
    placement_dict = {
        'assetId': asset['assetId'],
        'position': {'x': x, 'y': y, 'z': z},
        'rotation': rotation,
        'scale': {'x': scale, 'y': scale, 'z': scale}
    }
    return placement_dict


def procedurally_place(placement_map, ecotope):
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
