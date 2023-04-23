import json
import numpy as np
from PIL import Image
import pyglet
from pyglet.gl import *
from pyglet.window import key
from pyglet.math import Vec3
import sys


from camera import FPSCamera
from constants import *
from terrain import Terrain
import terrain
import utils


batch = pyglet.graphics.Batch()
draw_modes_map = {
    key.M: terrain.DRAW_MODE_WIREFRAME, key.N: terrain.DRAW_MODE_NORMALS
}


class Window(pyglet.window.Window):
    def __init__(self, debug_mode=False):
        super().__init__(caption="Pictorial Map", vsync=False)
        # Load map names
        with open(MAPS_FILENAME, 'r') as f:
            cities = json.load(f)
        option = int(input(utils.menu_str(cities))) - 1
        # option = 2
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
        self.mode = DEBUG_MODE if debug_mode else NORMAL_MODE
        self.orthographic_view = utils.OrthographicView(self)

    def on_key_press(self, symbol, modifiers):
        if symbol in draw_modes_map:
            draw_mode = draw_modes_map[symbol]
            if self.terrain.draw_mode == draw_mode:
                self.terrain.draw_mode = terrain.DRAW_MODE_SURFACE
            else:
                self.terrain.draw_mode = draw_mode
        super().on_key_press(symbol, modifiers)

    def on_draw(self, **kwargs):
        glClearColor(135 / 255.0, 206 / 255.0, 235 / 255.0, 1.0)
        self.clear()
        glPolygonMode(GL_FRONT_AND_BACK, self.terrain.polygon_mode)
        batch.draw()
        if self.mode == DEBUG_MODE:
            with self.orthographic_view:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                fps_display.draw()


if __name__ == '__main__':
    window = Window(debug_mode=True)
    cam_dist = 100 + window.terrain.size / 2
    camera = FPSCamera(
        window,
        position=Vec3(
            cam_dist, cam_dist, 0
        )
    )
    fps_display = pyglet.window.FPSDisplay(window=window)
    pyglet.app.run()
