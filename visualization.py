import json
import numpy as np
from PIL import Image
import pyglet
from pyglet.window import key
from pyglet.math import Vec3
import sys


from camera import FPSCamera
from constants import *
from terrain import Terrain
import utils


batch = pyglet.graphics.Batch()


class Window(pyglet.window.Window):
    def __init__(self):
        super().__init__()
        # Load map names
        with open(MAPS_FILENAME, 'r') as f:
            cities = json.load(f)
        # option = int(input(utils.menu_str(cities))) - 1
        option = 2
        if option == EXIT_CODE:
            sys.exit("You selected to exit the program")
        chosen_option = cities[option].lower()

        timer = utils.Timer()
        timer.start()
        # Load map config
        config_path = f"assets/{chosen_option}/{CONFIG_FILENAME}"
        with open(config_path, 'r') as f:
            config = json.load(f)
        # Load height map
        height_map_img = Image.open(
            f'assets/{chosen_option}/{HEIGHT_MAP_FILENAME}'
        ).convert('L')
        height_map = np.asarray(height_map_img) / 255 * config['maxHeight']
        # Load diffuse map
        diffuse_map = pyglet.resource.texture(
            f'assets/{chosen_option}/{SURFACE_TEXTURE}'
        )
        # Create terrain
        self.terrain = Terrain(
            config['mapSize'], config['maxHeight'], height_map,
            diffuse_map, batch=batch
        )
        timer.stop()
        print(f"Elapsed time generating terrain was {timer}")

    def on_key_press(self, symbol, modifiers):
        if symbol == key.N:
            self.terrain.is_in_debug_mode = not self.terrain.is_in_debug_mode
        super().on_key_press(symbol, modifiers)

    def on_draw(self, **kwargs):
        self.clear()
        batch.draw()


if __name__ == '__main__':
    window = Window()
    camera = FPSCamera(window, position=Vec3(460, 405, 28))
    pyglet.app.run()
