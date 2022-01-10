import numpy as np
from PIL import Image


from constants import *
import utils
from utils import ProgressBar


def create_surface_tex(app, is_2d=True):
    """
    Create a texture for the terrain using information from config of the map.
    Args:
        app(App): An app object that has the information of a map.
        is_2d(bool): Wheter this texture is for 2D top-view or 3D

    Returns:
        tuple: A tuple with an ndarray texture for terrain and its normal map.
    """
    texture_size = int(
        round(app.config['mapSize'] / app.config['heightMapPixelSize'])
    )
    total_count = texture_size
    bar = ProgressBar("Creating", max=total_count)
    # Load noise and resize to the map size
    noise_img = Image.open(f"{ASSETS_DIR}/perlin_noise.png")
    if noise_img.width != texture_size:
        noise_img.resize([texture_size, texture_size])
    noise_arr = np.array(noise_img) / MAX_COLOR     # Note: this is from 0 to 1
    height_arr = np.array(app.height_map)
    surface_tex = np.zeros(
        [texture_size, texture_size, COLOR_CHANNELS], dtype=np.uint8
    )
    normal_map = np.array(app.normal_map, dtype=np.uint8)
    water_normals_img = Image.open(f"{ASSETS_DIR}/waternormals.jpg")
    water_normals = np.array(water_normals_img, dtype=np.uint8)
    road_arr = np.array(app.road_map)
    for j in range(texture_size):
        for i in range(texture_size):
            u = i / texture_size
            v = j / texture_size
            noise = utils.blerp(u, v, noise_arr)
            height = height_arr[i, j] / MAX_COLOR * app.config['maxHeight']
            if height <= app.config['waterHeight']:
                # Case water
                if is_2d:
                    normal_map[i, j] = utils.blerp(u, v, water_normals)
                    color = np.array(app.config['waterColor'])
                else:
                    sand_color = np.array(app.config['sandColor'])
                    color = utils.lerp(
                        sand_color * 0.8, sand_color * 1.2, noise
                    )
            elif height < app.config['sandHeight']:
                # Case sand
                sand_color = np.array(app.config['sandColor'])
                color = utils.lerp(sand_color * 0.8, sand_color * 1.2, noise)
            else:
                # Case normal terrain
                road_value = road_arr[i, j] / MAX_COLOR
                road_color = np.array(app.config['roadColor'])
                light = np.array(app.config['groundColor'])
                dark = np.array(app.config['darkColor'])
                ground_color = utils.lerp(light, dark, noise)
                color = utils.lerp(road_color, ground_color, road_value)
            surface_tex[i, j] = color.astype(np.uint8)
        bar.next()
    bar.finish()
    return surface_tex, normal_map
