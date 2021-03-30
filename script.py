import json
import numpy as np
from PIL import Image

# Local modules
import dithering
import utils


DENSITY_FILENAME = "density_map.png"
PLACEMENT_MAP_FILENAME = "placement_map.jpg"
PLACEMENT_FILENAME = "placement.json"
ECOTOPE_FILENAME = "ecotope.json"
MAX_COLOR = 255
MAX_QUALITY = 95
# Allow only -+10% offset in position
MAX_POS_OFFSET = 0.2
# Only allow up to 10% scale
MAX_SCALE = 0.1
# Allowed rotations
ROTATIONS = [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]
# Each pixel will represent 7 mt square
pixel_size = 7
rng = np.random.default_rng()
cities = ["Shechem", "Jerusalem"]
chosen_option = "shechem"


def discretize_density(density_map):
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
    placement_map_path = f"assets/{chosen_option}/{PLACEMENT_MAP_FILENAME}"
    output_img.save(placement_map_path, quality=MAX_QUALITY)
    print(f"Image saved in {placement_map_path}.jpg")
    timer.stop()
    print(f"Total time spent: {timer}")
    return output


def procedurally_place(placement_map, ecotope):
    h, w = placement_map.shape
    # Sort ecotope array
    sorted_ecotope = sorted(ecotope, key=lambda e: e['footprint'], reverse=True)
    # Iterate placing assets
    placement_json = []
    # Iterate on pixels
    for j in range(h):
        for i in range(w):
            if placement_map[j][i]:
                p = rng.random()
                accumulated_prob = 0
                for asset in sorted_ecotope:
                    accumulated_prob += asset['probability']
                    if p <= accumulated_prob:
                        # Place object
                        placement_map[j][i] = 0
                        position_offset = (
                            (-0.5 + rng.random(2)) * MAX_POS_OFFSET
                        )
                        x = (i - w // 2 + 0.5 + position_offset[0]) * pixel_size
                        y = 0
                        z = (j - h // 2 + 0.5 + position_offset[1]) * pixel_size
                        # rotation = rng.choice(ROTATIONS)
                        rotation = 0
                        scale_offset = rng.random() * MAX_SCALE
                        scale = 1 - scale_offset
                        placement_dict = {
                            'assetId': asset['assetId'],
                            'position': {
                                'x': x, 'y': y, 'z': z
                            },
                            'rotation': rotation,
                            'scale': {
                                'x': scale, 'y': scale, 'z': scale
                            }
                        }
                        placement_json.append(placement_dict)
                        break
    return placement_json


def main():
    global chosen_option
    option = int(input(utils.menu_str(cities))) - 1
    chosen_option = cities[option].lower()
    density_map_file = f"assets/{chosen_option}/density_map.png"
    # Open Density Map
    img = Image.open(density_map_file)
    grayscale = img.convert('L')
    density_map = np.array(grayscale, dtype=float) / MAX_COLOR
    # Discretize
    placement_map = discretize_density(density_map)
    # Load ecotope
    # Read Ecotope JSON file
    ecotope_path = f"assets/{chosen_option}/{ECOTOPE_FILENAME}"
    with open(ecotope_path, 'r') as f:
        ecotope = json.load(f)
    # Procedurally place
    placement_json = procedurally_place(placement_map, ecotope)
    # Save placement array in JSON
    placement_path = f"assets/{chosen_option}/{PLACEMENT_FILENAME}"
    with open(placement_path, 'w') as f:
        json.dump(placement_json, f)
    print(f"Finished writing placement json file in {placement_path}")


if __name__ == '__main__':
    main()
