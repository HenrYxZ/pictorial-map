import json
import numpy as np
from PIL import Image

# Local modules
import dithering
import utils


DENSITY_FILENAME = "density_map.png"
PLACEMENT_MAP_FILENAME = "placement_map.jpg"
PLACEMENT_FILENAME = "js/placement.json"
ASSETS_FILENAME = "js/assets.json"
ECOTOPE_FILENAME = "ecotope.json"
MAX_COLOR = 255
MAX_QUALITY = 95
# Only allow up to 20% scale
MAX_SCALE = 0.2
# Each pixel will represent 5 mt square
pixel_size = 5
rng = np.random.default_rng()


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
    output_img.save(PLACEMENT_MAP_FILENAME, quality=MAX_QUALITY)
    print(f"Image saved in {PLACEMENT_MAP_FILENAME}.jpg")
    timer.stop()
    print(f"Total time spent: {timer}")
    return output


def procedurally_place(placement_map):
    global pixel_size
    h, w = placement_map.shape
    # Read Ecotope JSON file
    with open(ECOTOPE_FILENAME, 'r') as f:
        ecotope = json.load(f)
    # Sort ecotope array
    sorted_ecotope = sorted(ecotope, key=lambda x: x['footprint'], reverse=True)
    # Iterate placing assets
    footprint = sorted_ecotope[0]['footprint']
    placement_json = []
    for asset in sorted_ecotope:
        new_footprint = asset['footprint']
        ratio = int(footprint // new_footprint)
        if ratio > 1:
            footprint = new_footprint
            # resize to placement map
            h *= ratio
            w *= ratio
            pixel_size /= ratio
            placement_map = utils.resize(placement_map, ratio)
        for j in range(h):
            for i in range(w):
                if placement_map[j][i]:
                    p = rng.random()
                    if p < asset['probability']:
                        # Place object
                        placement_map[j][i] = 0
                        position_offset = rng.random(2)
                        x = (i - w // 2 + 0.5 + position_offset[0]) * pixel_size
                        y = 0
                        z = (j - h // 2 + 0.5 + position_offset[1]) * pixel_size
                        rotation = rng.random() * 2 * np.pi
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
    return placement_json


def main():
    # Open Density Map
    img = Image.open(DENSITY_FILENAME)
    grayscale = img.convert('L')
    density_map = np.array(grayscale, dtype=float) / MAX_COLOR
    # Discretize
    placement_map = discretize_density(density_map)
    # Procedurally place
    placement_json = procedurally_place(placement_map)
    # Save placement array in JSON
    with open(PLACEMENT_FILENAME, 'w') as f:
        json.dump(placement_json, f)
    print(f"Finished writing placement json file in {PLACEMENT_FILENAME}")


if __name__ == '__main__':
    main()
