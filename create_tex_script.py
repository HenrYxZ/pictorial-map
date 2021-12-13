import numpy as np
import json

# Local modules
import utils

CONFIG_FILENAME = "config.json"
MAPS_FILENAME = "maps.json"
SIZE = 1280


def main():
    maps_path = f"js/maps.json"
    with open(maps_path, 'r') as f:
        cities = json.load(f)
    option = int(input(utils.menu_str(cities))) - 1
    city = cities[option]
    config_path = f"assets/{city}/{CONFIG_FILENAME}"
    with open(config_path, 'r') as f:
        config = json.load(f)
    color = np.array(config['groundColor'])
    if config.get('darkColor'):
        dark_color = np.array(config['darkColor'])
    else:
        dark_color = 0.8 * color
    noise_path = "assets/perlin_noise.png"
    img = utils.create_texture_from_noise(color, SIZE, noise_path, dark_color)
    img.save(f'assets/{city}/ground.png')


if __name__ == '__main__':
    main()
