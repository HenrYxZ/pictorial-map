# Local modules
import numpy as np

from utils import create_texture_from_noise


def main():
    city = "shechem"
    color = np.array([161, 153, 95])
    img = create_texture_from_noise(color, "assets/perlin_noise.png")
    img.save(f'assets/{city}/ground.png')


if __name__ == '__main__':
    main()
