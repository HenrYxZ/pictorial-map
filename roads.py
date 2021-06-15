import numpy as np
from PIL import Image, ImageFilter


MAX_COLOR = 255
# DX = [
#     0, 0, 0,
#     -1, 0, 1,
#     0, 0, 0
# ]
# DY = [
#     0, 1, 0,
#     0, 0, 0,
#     0, -1, 0
# ]
DX = [
    0, 0, 0, 0, 0,
    0, 0, 0, 0, 0,
    -1, 0, 0, 0, 1,
    0, 0, 0, 0, 0,
    0, 0, 0, 0, 0
]
DY = [
    0, 0, 1, 0, 0,
    0, 0, 0, 0, 0,
    0, 0, 0, 0, 0,
    0, 0, 0, 0, 0,
    0, 0, -1, 0, 0
]
DEFAULT_KERNEL_SIZE = (5, 5)
DEFAULT_COMPARISON_DISTANCE = 5
RGB_CHANNELS = 3


def dilate(img):
    filter_size = 3
    dilated = img.filter(ImageFilter.MaxFilter(filter_size))
    return dilated


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
    # Iterate on possible colors.
    # final_img = road_map
    final_arr = np.array(road_map, dtype=np.uint8)
    w, h = final_arr.shape
    current_img = road_map
    for current_color in range(MAX_COLOR - 1, 1, -1):
        dilated_img = dilate(current_img)
        colored_arr = np.array(
            np.array(dilated_img) / MAX_COLOR * current_color, dtype=np.uint8
        )
        current_img = Image.fromarray(colored_arr)
        for i in range(w * h):
            row = i // w
            col = i - row * w
            final_arr[row][col] = max(
                final_arr[row][col], colored_arr[row][col]
            )
    # Invert the colors
    final_arr = MAX_COLOR - final_arr
    return final_arr


def create_from_kernel(img, kernel):
    new_img = img.filter(ImageFilter.Kernel(DEFAULT_KERNEL_SIZE, kernel))
    new_arr = np.asarray(new_img)
    return new_arr


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
        difference = next_pixel - previous_pixel
        derivative[j][i] = difference / 2 + MAX_COLOR / 2
    return derivative


def create_dx(img_arr):
    def get_previous(x, i, j, distance): return x[j][i - distance // 2]
    def get_next(x, i, j, distance): return x[j][i + distance // 2]
    dx = create_derivative(img_arr, get_previous, get_next)
    return dx


def create_dy(img_arr):
    def get_previous(x, i, j, distance): return x[j - distance // 2][i]
    def get_next(x, i, j, distance): return x[j + distance // 2][i]
    dy = create_derivative(img_arr, get_previous, get_next)
    return dy


def create_orient_map(dist_map):
    """
    Create a numpy array where each element is a RGB pixel. R means
    difference in x, G means difference in y and B is irrelevant.

    Args:
        dist_map(ndarray): 2D array where each element is the distance to the
            nearest road.
    Returns:
         ndarray: The orient map with dx in R, dy in G and MAX_COLOR // 2 in B
    """
    h, w = dist_map.shape
    orient_map = np.zeros([h, w, RGB_CHANNELS], dtype=np.uint8)
    # create dx & dy
    dist_map_img = Image.fromarray(dist_map)
    dist_map = np.asarray(dist_map_img)
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
        orient_map[row][col][2] = 0
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
