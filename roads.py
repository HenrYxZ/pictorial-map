import numpy as np
from PIL import Image

MAX_COLOR = 255
DEFAULT_COMPARISON_DISTANCE = 5
RGB_CHANNELS = 3


def high_pass(arr, num):
    """
    Create a new 2D array iterating the input and for each element if it is
    non-zero it will be num, else 0.
    Args:
        arr(ndarray): Input array
        num(int): Number to leave in each cell after that passes the
            high pass.
    Returns:
        list: 2D array with a high pass filter
    """
    new_arr = [
        [num if element else 0 for element in row] for row in arr
    ]
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


def create_derivative(
        img_arr, get_previous, get_next, distance=DEFAULT_COMPARISON_DISTANCE
):
    """
    Create a derivative array from an image
    Args:
        img_arr(ndarray): Input image array
        get_previous(function): Function to obtain the previous pixel in the
            form f(img, i, j)
        get_next(function): Function to obtain the next pixel in the
            form f(img, i, j)
        distance(int): Distance in pixels between the previous and the next
    Returns:
         ndarray: An image array with the derivative
    """
    h, w = img_arr.shape
    derivative = np.zeros([h, w])
    for count in range(h * w):
        i = count % (w - distance)
        j = (count // w) % (h - distance)
        previous_pixel = get_previous(img_arr, i, j, distance)
        next_pixel = get_next(img_arr, i, j, distance)
        difference = (next_pixel - previous_pixel) * 10
        derivative[j][i] = int(difference + MAX_COLOR / 2)
    return derivative


def create_dx(img_arr):
    def get_previous(x, i, j, distance): return x[j][i - distance // 2]
    def get_next(x, i, j, distance): return x[j][i + distance // 2]
    dx = create_derivative(img_arr, get_previous, get_next)
    return dx


def create_dy(img_arr):
    def get_previous(x, i, j, distance): return x[j + distance // 2][i]
    def get_next(x, i, j, distance): return x[j - distance // 2][i]
    dy = create_derivative(img_arr, get_previous, get_next)
    return dy


def create_orient_map(dist_map):
    """
    Create a numpy array where each element is a RGB pixel. R means
    difference in x, G means difference in y and B is irrelevant.

    Args:
        dist_map(ndarray): 2D array where each element is the distance to the
            nearest road. It has to be in type float!
    Returns:
         ndarray: The orient map with dx in R, dy in G and MAX_COLOR // 2 in B
    """
    h, w = dist_map.shape
    orient_map = np.zeros([h, w, RGB_CHANNELS], dtype=np.uint8)
    # create dx & dy
    dx = create_dx(dist_map)
    dy = create_dy(dist_map)
    dx_img = Image.fromarray(np.array(dx, dtype=np.uint8))
    dy_img = Image.fromarray(np.array(dy, dtype=np.uint8))
    dx_img.save('debug/shechem/dx.png')
    dy_img.save('debug/shechem/dy.png')
    for i in range(h * w):
        row = i // w
        col = i - row * w
        orient_map[row][col][0] = dx[row][col]
        orient_map[row][col][1] = dy[row][col]
        orient_map[row][col][2] = MAX_COLOR
    return orient_map


def test_img():
    road_map = Image.open('assets/shechem/road_map.png').convert('L')
    dist_map = create_dist_map(road_map)
    dist_map_img = Image.fromarray(dist_map)
    dist_map_img.save('dist_map.png')
    # create orient map
    orient_map = create_orient_map(dist_map)
    orient_map_img = Image.fromarray(orient_map)
    orient_map_img.save('orient_map.png')


if __name__ == '__main__':
    test_img()
