import numpy as np
from PIL import Image
import json

# Local modules
from app import App
from constants import *
from surface import create_surface_tex
import utils


def main(is_2d=True):
    app = App()
    surface_arr, normal_arr = create_surface_tex(app, is_2d=is_2d)
    surface_img = Image.fromarray(surface_arr)
    surface_img.save("surface.png")
    normal_map = Image.fromarray(normal_arr)
    normal_map.save("normal_map.png")


def create_water_map():
    app = App()
    water_height = app.config['waterHeight']
    height_arr = np.array(app.height_map) / MAX_COLOR
    height_arr = height_arr * app.config['maxHeight']
    water_arr = height_arr <= water_height
    water_img = Image.fromarray(water_arr)
    water_img.save("water_map.png")


def create_light_and_dark():
    filename = "surface.png"
    img = Image.open(filename)
    img_arr = np.array(img)
    light = np.asarray(img_arr * 1.3).clip(0, MAX_COLOR).astype(np.uint8)
    light_img = Image.fromarray(light)
    dark = np.asarray(img_arr * 0.7).clip(0, MAX_COLOR).astype(np.uint8)
    dark_img = Image.fromarray(dark)
    light_img.save("C1.png")
    dark_img.save("C0.png")


if __name__ == '__main__':
    menu_str = utils.menu_str([
        "Surface 2D", "Surface 3D", "Water Map", "Light & Dark"
    ])
    option = int(input(menu_str))
    if option == 1:
        main()
    elif option == 2:
        main(is_2d=False)
    elif option == 3:
        create_water_map()
    elif option == 4:
        create_light_and_dark()
    else:
        exit()
