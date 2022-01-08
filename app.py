import json
import pyglet
import sys

# Local modules
from constants import *
import utils

class App:
    def __init__(self):
        # # Load map names
        # with open(MAPS_FILENAME, 'r') as f:
        #     cities = json.load(f)
        # option = int(input(utils.menu_str(cities))) - 1
        # if option == EXIT_CODE:
        #     sys.exit("You selected to exit the program")
        # chosen_option = cities[option].lower()
        chosen_option ="sf-sm"

        # Load assets
        with open(ASSETS_FILENAME, 'r') as f:
            self.assets_json = json.load(f)

        # Load config
        config_path = f"{ASSETS_DIR}/{chosen_option}/{CONFIG_FILENAME}"
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Load placements
        placement_path = f"{ASSETS_DIR}/{chosen_option}/{PLACEMENT_FILENAME}"
        with open(placement_path, 'r') as f:
            self.placements_json = json.load(f)

        # Load surface
        # surface_tex_path = f"{ASSETS_DIR}/{chosen_option}/{SURFACE_TEXTURE}"
        surface_tex_path = f"2d/{SURFACE_TEXTURE}"
        self.surface_texture = pyglet.image.load(surface_tex_path)

        # Load height map
        height_map_path = f"2d/{HEIGHT_MAP_FILENAME}"
        self.height_map = pyglet.image.load(height_map_path)
