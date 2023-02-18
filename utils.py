from PIL import Image
from progress.bar import Bar
import numpy as np
import os
import os.path
import time

COLOR_CHANNELS = 3
MAX_COLOR = 255
COLOR_BLACK = np.zeros(3)


def open_image(img_filename):
    img = Image.open(img_filename)
    img_arr = np.array(img)
    return img_arr


def normalize(arr):
    """
    Normalize a vector using numpy.
    Args:
        arr(darray): Input vector
    Returns:
        darray: Normalized input vector
    """
    norm = np.linalg.norm(arr)
    if norm == 0:
        return arr
    return arr / norm


def distance(p1, p2):
    """
    Get the distance between points p1 and p2
    Args:
        p1(ndarray): Point 1
        p2(ndarray): Point 2
    Returns:
         float: Distance
    """
    dist = np.linalg.norm(p1 - p2)
    return dist


def humanize_time(secs):
    minutes, secs = divmod(secs, 60)
    hours, minutes = divmod(minutes, 60)
    return '%02d:%02d:%02d' % (hours, minutes, secs)


def degrees2radians(degrees):
    return (degrees / 360) * 2 * np.pi


def radians2degrees(radians):
    return (radians / (2 * np.pi)) * 360


def normalize_color(color):
    return color / MAX_COLOR


def lerp(a, b, t):
    return t * a  + (1 - t) * b


def blerp(u, v, img_arr):
    if len(img_arr.shape) == 3:
        height, width, _ = img_arr.shape
    else:
        height, width = img_arr.shape
    x = u * width
    y = v * height
    return sample_2d(x, y, img_arr)


def sample_2d(x, y, img_arr):
    if len(img_arr.shape) == 3:
        height, width, _ = img_arr.shape
    else:
        height, width = img_arr.shape
    # Flip y value to go from top to bottom
    y = height - y
    # Interpolate values of pixel neighborhood of x and y
    i = int(np.round(x))
    j = int(np.round(y))
    if i == 0 or j == 0 or i >= width or j >= height:
        if i >= width:
            i -= width
        if j >= height:
            j -= height
        return img_arr[j][i]
    # t and s are interpolation parameters that go from 0 to 1
    t = x - i + 0.5
    s = y - j + 0.5
    # Bilinear interpolation
    color = (
        img_arr[j - 1][i - 1] * (1 - t) * (1 - s)
        + img_arr[j - 1][i] * t * (1 - s)
        + img_arr[j][i - 1] * (1 - t) * s
        + img_arr[j][i] * t * s
    )
    return color


def resize(img_arr, ratio):
    # resize img_arr with 2D
    if len(img_arr.shape) == 3:
        h, w, _ = img_arr.shape
    else:
        h, w = img_arr.shape
    new_h = h * ratio
    new_w = w * ratio
    new_img_arr = np.zeros([new_h, new_w])
    for j in range(new_h):
        for i in range(new_w):
            new_img_arr[j][i] = img_arr[j // ratio][i // ratio]
    return new_img_arr


def menu_str(options):
    s = "Select an option:\n"
    for opt_num, opt in enumerate(options, start=1):
        s += f"[{opt_num}] for {opt}\n"
    s += "[0] to exit\n"
    return s


def exist_or_create(dir_path):
    """
    Check if the given directory path exist, if not creates it

    Args:
        dir_path(string): The path for the directory
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


def create_texture_from_noise(
        color, size, noise_img_path, dark_color=COLOR_BLACK
):
    """
    Create a 2D image texture by multiplying a given color with a grayscale
    noise.
    Args:
        color(ndarray): RGB color
        size(int): length of one side in pixels
        noise_img_path(str): Path for the noise image
        dark_color(ndarray): RGB for dark color to interpolate

    Returns:
        Image: 2D image texture
    """
    noise_img = Image.open(noise_img_path)
    if noise_img.size[0] != size:
        noise_img = noise_img.resize([size, size])
    noise_arr = np.asarray(noise_img) / MAX_COLOR
    combined_array = noise_arr * color + (1 - noise_arr) * dark_color
    final_array = np.array(combined_array, dtype=np.uint8)
    output_img = Image.fromarray(final_array)
    return output_img


def create_light_and_dark_image(img_path):
    img = Image.open(img_path)
    dark_img = img.point(lambda p: p * 0.6)
    light_img = img.point(lambda p: p * 1.3)
    dark_img.save('C0.png')
    light_img.save('C1.png')


class Timer:
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.elapsed_time = 0

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time

    def __str__(self):
        return humanize_time(self.elapsed_time)


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def to_dict(self):
        return {
            'x': float(np.round(self.x, 3)),
            'y': float(np.round(self.y, 3)),
            'z': float(np.round(self.z, 3))
        }

    @staticmethod
    def dict_to_arr(point_dict):
        arr = np.array([point_dict['x'], point_dict['y'], point_dict['z']])
        return arr


class ProgressBar(Bar):
    suffix = '%(percent)d%% [%(elapsed_td)s / %(eta_td)s]'
    check_tty = False
