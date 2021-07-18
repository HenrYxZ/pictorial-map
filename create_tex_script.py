# Local modules
import numpy as np

from utils import create_texture_from_noise


def main():
    city = "jerusalem"
    color = np.array([235, 230, 183])
    dark_color = 0.8 * color
    size = 640
    noise_path = "assets/perlin_noise.png"
    img = create_texture_from_noise(color, size, noise_path, dark_color)
    img.save(f'assets/{city}/ground.png')


if __name__ == '__main__':
    main()
