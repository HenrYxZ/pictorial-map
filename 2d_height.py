import numpy as np
import pyglet
from PIL import Image
from pyglet.gl import *
from pyglet import shapes
from pyglet.window import key

# Local imports
from app import App
from constants import *
from models import Placement
import utils

# Config
WIDTH = 640
HEIGHT = 640
COLOR_VARIATION = 0.1


main_window = pyglet.window.Window(WIDTH, HEIGHT)
batch = pyglet.graphics.Batch()
rng = np.random.default_rng()


def get_height_by_id(asset_id):
    if asset_id == 2:
        # color tree
        new_height = 3
    elif asset_id == 3:
        # color gray rock
        new_height = 1
    else:
        # color building
        new_height = 2.4
    normalized_height = new_height / max_height
    color = np.clip(normalized_height * MAX_COLOR, 0, MAX_COLOR).astype(int)
    return color


def create_shape(asset, x, y, color):
    if asset.shape == CIRCLE_SHAPE:
        radius = asset.footprint / 2
        # (make sure to transform world units to screen units)
        return shapes.Circle(x, y, radius, color=color)
    else:
        return shapes.Rectangle(
            x, y, width=8, height=4, color=color
        )


def draw_height(placement):
    # draw shape in the place
    x = placement.position[0] + map_size / 2
    y = placement.position[2] + map_size / 2
    # flip y coord
    y = map_size - y
    asset = placement.asset
    if (
            placement.rotation == FULL_ROTATION or
            placement.rotation == RANDOM_ROTATION
    ):
        rotation = rng.uniform(0, 360)
    else:
        rotation = utils.radians2degrees(float(placement.rotation))
    color = get_height_by_id(asset.id)
    height_map_sample = utils.sample_2d(x, y, height_arr) * MAX_COLOR
    color = np.clip(color + height_map_sample, 0, MAX_COLOR).astype(int)
    shape = create_shape(asset, x, y, color)
    shape.rotation = rotation
    shape.draw()


@main_window.event
def on_draw():
    main_window.clear()
    # draw height map
    background.draw()
    # draw each individual asset from placement.json
    if app.placements_json is not None:
        for placement_json in app.placements_json:
            placement = Placement(placement_json, app.assets_json)
            draw_height(placement)


@main_window.event
def on_key_press(symbol, _):
    if symbol == key.S:
        pyglet.image.get_buffer_manager().get_color_buffer().save('h.png')


if __name__ == '__main__':
    app = App()
    map_size = app.config['mapSize']
    max_height = app.config['maxHeight']
    background = pyglet.sprite.Sprite(app.height_map)
    height_img = Image.open('2d/height_map.png')
    height_arr = np.array(height_img) / MAX_COLOR
    pyglet.app.run()
