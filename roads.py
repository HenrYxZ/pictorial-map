import numpy as np
from PIL import Image

MAX_COLOR = 255
DEFAULT_COMPARISON_DISTANCE = 2
RGB_CHANNELS = 3


def high_pass(arr, num):
    """
    Create a new 2D array iterating the input and for each element if it is
    greater than the threshold it will be num, else 0.
    Args:
        arr(ndarray): Input array
        num(int): Number to leave in each cell after that passes the high pass
    Returns:
        list: 2D array with a high pass filter
    """
    threshold = MAX_COLOR / 20
    new_arr = np.where(arr > threshold, num, 0)
    return new_arr


def add_neighbors(closed, j, i, open_pixels):
    h, w = closed.shape
    rows = [j - 1, j, j + 1]
    cols = [i - 1, i, i + 1]
    for row in rows:
        for col in cols:
            if 0 <= row < h and 0 <= col < w and not closed[row][col]:
                closed[row][col] = True
                open_pixels.append((row, col))


def flood(img_arr):
    """
    Create an inverted Djikstra map
    Args:
        img_arr(ndarray): input image array (binary)

    Returns:
        ndarray: Image with dilation applied
    """
    h, w = img_arr.shape
    new_arr = MAX_COLOR - img_arr
    closed = np.zeros([h, w], dtype=bool)
    road_pixels = []
    open_pixels = []
    # First pass: Add roads to closed
    for counter in range(h * w):
        i = counter % w
        j = counter // w
        if new_arr[j][i] == 0:
            closed[j][i] = True
            road_pixels.append((j, i))
    # Second pass: Add border to open
    for j, i in road_pixels:
        add_neighbors(closed, j, i, open_pixels)
    # Third pass: Iterate until 255 colors adding new boundary each time
    for color in range(1, MAX_COLOR - 1):
        next_open = []
        for j, i in open_pixels:
            new_arr[j][i] = color
            add_neighbors(closed, j, i, next_open)
        open_pixels = next_open
    # Last pass: Paint last pixels
    for j, i in open_pixels:
        new_arr[j][i] = MAX_COLOR - 1
    return new_arr


def create_dist_map(road_map):
    """
    Create a map where each pixel is the distance to the nearest road, up to 255
    pixels.
    Args:
        road_map(ndarray): Map where white means roads and black is no roads.
            The map has to have a value for white equal to MAX_COLOR.
    Returns:
         ndarray: The map with the distances from the roads
    """
    final_arr = np.array(road_map, dtype=np.uint8)
    # transform array to binary
    final_arr = np.array(high_pass(final_arr, MAX_COLOR), dtype=np.uint8)
    final_arr = flood(final_arr)
    return final_arr
