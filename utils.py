from PIL import Image
import numpy as np
import os
import os.path
import time


MAX_COLOR = 255


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
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)


def degrees2radians(degrees):
    return (degrees / 360) * 2 * np.pi


def normalize_color(color):
    return color / MAX_COLOR


def blerp(img_arr, x, y):
    # Interpolate values of pixel neighborhood of x and y
    i = int(np.round(x))
    j = int(np.round(y))
    # But not in the borders
    height, width, _ = img_arr.shape
    # Flip y value to go from top to bottom
    y = height - y
    if i == 0 or j == 0 or i == width or j == height:
        if i == width:
            i -= 1
        if j == height:
            j -= 1
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
    return s


def exist_or_create(dir_path):
    """
    Check if the given directory path exist, if not creates it

    Args:
        dir_path(string): The path for the directory
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


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
