import numpy as np


THRESHOLD_MAP = (1 / 16) * np.array([
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5]
])


def floyd_steinberg_dithering(img_arr):
    h, w = img_arr.shape
    # output = np.copy(img_arr) + np.random.random_sample([h, w])
    output = np.copy(img_arr)
    for j in range(h):
        for i in range(w):
            x = i if j % 2 == 0 else w - 1 - i
            original_pixel = output[j][x]
            # new_pixel = find_closest_color(original_pixel, palette)
            new_pixel = round(original_pixel)
            output[j][x] = new_pixel
            error = original_pixel - new_pixel
            if j < h - 1 and 0 < x < w - 1 and j % 2 == 0:
                output[j][x + 1] += error * 7 / 16
                output[j + 1][x - 1] += error * 3 / 16
                output[j + 1][x] += error * 5 / 16
                output[j + 1][x + 1] += error * 1 / 16
            if j < h - 1 and 0 < x < w - 1 and j % 2 == 1:
                output[j][x - 1] += error * 7 / 16
                output[j + 1][x - 1] += error * 3 / 16
                output[j + 1][x] += error * 5 / 16
                output[j + 1][x - 1] += error * 1 / 16
    return (np.clip(output, 0, 1) * 255).astype(np.uint8)


def ordered_dithering(img_arr):
    h, w = img_arr.shape
    output = np.zeros([h, w], dtype=bool)
    for j in range(h):
        for i in range(w):
            if img_arr[j][i] <= THRESHOLD_MAP[j % 4][i % 4]:
                output[j][i] = 0
            else:
                output[j][i] = 1
    return output
