import numpy as np
from utils import rotation_matrice_z, rotation_matrice_y


def generate_donut_mesh(R, r, scale_screen, num_pixels):
    # parameters
    dx = scale_screen / num_pixels
    safety_factor = 1e-1
    d_theta = safety_factor * dx / r
    d_phi = safety_factor * dx / (R + r)
    R_z = rotation_matrice_z(d_theta)
    R_y = rotation_matrice_y(d_phi)

    e_x = np.array([1.0, 0.0, 0.0])
    vertices = np.empty((0, 3))
    normals = np.empty((0, 3))

    # initial circle
    buffer_n = np.copy(e_x)
    for idx in range(int(2 * np.pi / d_theta)):
        buffer_n = (R_z @ buffer_n).T
        v = R * e_x + r * buffer_n
        vertices = np.vstack((vertices, v))
        normals = np.vstack((normals, buffer_n))
    circle, circle_normals = np.copy(vertices), np.copy(normals)

    # rotate circle
    for idx in range(int(2 * np.pi / d_phi)):
        circle = (R_y @ circle.T).T
        circle_normals = (R_y @ circle_normals.T).T
        vertices = np.vstack((vertices, circle))
        normals = np.vstack((normals, circle_normals))

    return vertices, normals
