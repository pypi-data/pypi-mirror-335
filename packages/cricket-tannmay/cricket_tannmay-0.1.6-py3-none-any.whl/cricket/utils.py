import numpy as np

color_ranges = {
    "green": [(35, 40, 40), (85, 255, 255)],
    "white": [(0, 0, 168), (172, 111, 255)],
    "orange": [(10, 100, 100), (25, 255, 255)],
    "yellow": [(25, 100, 100), (35, 255, 255)],
    "blue": [(100, 100, 50), (140, 255, 255)],
    "black": [(0, 0, 0), (180, 255, 50)],
    "pink": [(150, 50, 50), (170, 255, 255)],
    "red": [(0, 70, 50), (10, 255, 255)]
}


def calculate_angle(a, b, c):
    a = np.array(a)  # First point
    b = np.array(b)  # Midpoint
    c = np.array(c)  # Last point

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360.0 - angle

    return angle
