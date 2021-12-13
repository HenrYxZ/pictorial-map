import json
import numpy as np
import os
from PIL import Image

# Local modules
import roads

ASSETS_DIR = "2d"
JS_DIR = "js"
# Maps
DENSITY_FILENAME = "density_map.png"
DIST_MAP_FILENAME = "dist_map.png"
HEIGHT_MAP_FILENAME = "height_map.png"
ORIENT_MAP_FILENAME = "orient_map.png"
ROAD_MAP_FILENAME = "road_map.png"
# JSON
ASSETS_FILENAME = "assets.json"
CONFIG_FILENAME = "config.json"
ECOTOPES_FILENAME = "ecotopes.json"


class Placer:
    def __init__(self, map_name, config):
        self.map_name = map_name
        self.map_size = config['mapSize']
        # Load height map
        height_map_path = f"{ASSETS_DIR}/{self.map_name}/{HEIGHT_MAP_FILENAME}"
        if not os.path.isfile(height_map_path):
            print(f"Height map {height_map_path} not found")
        img = Image.open(height_map_path)
        height_map_img = img.convert('L')
        self.height_map = np.array(height_map_img, dtype=np.uint8)

        # Load road map
        road_map_path = f"{ASSETS_DIR}/{self.map_name}/{ROAD_MAP_FILENAME}"
        if not os.path.isfile(road_map_path):
            self.road_map = None
            self.dist_map = None
        else:
            self.road_map = Image.open(road_map_path).convert('L')
            self.dist_map = roads.create_dist_map(self.road_map)
        # Load ecotopes
        ecotopes_path = f"{ASSETS_DIR}/{self.map_name}/{ECOTOPES_FILENAME}"
        with open(ecotopes_path, 'r') as f:
            self.ecotopes = json.load(f)
        # Load assets
        assets_path = f"{JS_DIR}/{ASSETS_FILENAME}"
        with open(assets_path):
            self.assets = json.load(f)
