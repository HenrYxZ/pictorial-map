import json
import pyglet
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
        # Create terrain
        self.terrain = Terrain(
            size=config['mapSize'], max_height=config['maxHeight'], batch=batch
        )
        timer.stop()
        print(f"Elapsed time generating terrain was {timer}")

    def on_draw(self):
        self.clear()
        batch.draw()


if __name__ == '__main__':
    window = Window()
    camera = FPSCamera(window, position=Vec3(0, 3, 5))
    pyglet.app.run()
