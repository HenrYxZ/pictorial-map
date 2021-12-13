import numpy as np
import pyglet
from pyglet import shapes

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


def get_color_by_id(asset_id):
    if asset_id == 2:
        # color tree
        color = np.array([26, 135, 55])
    elif asset_id == 3:
        # color gray rock
        color = np.array([150, 150, 150])
    else:
        # color building
        color = np.array([227, 203, 138])
    color = random_variate(color)
    color = np.clip(color.round(), 0, 255).astype(int)
    return color


def create_shape(asset, x, y, color):
    if asset.shape == CIRCLE_SHAPE:
        radius = asset.footprint / 2
        # (make sure to transform world units to screen units)
        return shapes.Circle(x, y, radius, color=color)
    else:
        return shapes.Rectangle(x, y, width=8, height=4, color=color)


def random_variate(color):
    # random color variation
    coin = rng.random()
    if coin < 0.2:
        color = color * (1 + COLOR_VARIATION)
    elif coin < 0.5:
        color = color * (1 - COLOR_VARIATION)
    return color


def draw_asset(placement):
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
    color = get_color_by_id(asset.id)
    shape = create_shape(asset, x, y, color)
    shape.rotation = rotation
    shape.draw()



@main_window.event
def on_draw():
    main_window.clear()
    # blit terrain
    app.surface_texture.blit(0, 0)
    # draw each individual asset from placement.json
    if app.placements_json is not None:
        for placement_json in app.placements_json:
            placement = Placement(placement_json, app.assets_json)
            draw_asset(placement)
    batch.draw()
    print("drawing")


if __name__ == '__main__':
    app = App()
    map_size = app.config['mapSize']
    pyglet.app.run()
