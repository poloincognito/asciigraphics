import math
import numpy as np

DEBUG = False

luminance_string = " .,-~:;=!*#$@"


def luminance_to_char(luminance: float) -> str:
    """Returns a character from the luminance string based on the luminance."""
    return luminance_string[int(luminance * (len(luminance_string) - 1))]


def rotation_matrice_z(theta: float) -> np.ndarray:
    """Returns a 3D rotation matrix around the z-axis."""
    return np.array(
        [
            [math.cos(theta), -math.sin(theta), 0],
            [math.sin(theta), math.cos(theta), 0],
            [0, 0, 1],
        ]
    )


def rotation_matrice_y(phi: float) -> np.ndarray:
    """Returns a 3D rotation matrix around the y-axis."""
    return np.array(
        [
            [math.cos(phi), 0, math.sin(phi)],
            [0, 1, 0],
            [-math.sin(phi), 0, math.cos(phi)],
        ]
    )


def rotation_matrice_x(psi: float) -> np.ndarray:
    """Returns a 3D rotation matrix around the x-axis."""
    return np.array(
        [
            [1, 0, 0],
            [0, math.cos(psi), -math.sin(psi)],
            [0, math.sin(psi), math.cos(psi)],
        ]
    )


class Mesh:
    def __init__(self, vertices: np.ndarray, normals: np.ndarray):
        self.vertices = vertices
        self.normals = normals


class RotatableMesh(Mesh):  # the best practice would be to use an inteface here
    def rotate(self, angle: float, axis: str):
        if axis == "x":
            self.vertices = np.dot(self.vertices, rotation_matrice_x(angle))
            self.normals = np.dot(self.normals, rotation_matrice_x(angle))
        elif axis == "y":
            self.vertices = np.dot(self.vertices, rotation_matrice_y(angle))
            self.normals = np.dot(self.normals, rotation_matrice_y(angle))
        elif axis == "z":
            self.vertices = np.dot(self.vertices, rotation_matrice_z(angle))
            self.normals = np.dot(self.normals, rotation_matrice_z(angle))
        else:
            raise ValueError("Axis must be x, y or z")


class Screen:
    def __init__(self, width: int, scale: float = 1.0):
        self.width = width
        self.pixels = np.zeros((width, width))
        self.depth_buffer = np.full((width, width), np.inf)
        self.scale = scale

    def coord_to_idx(self, x: float, y: float) -> tuple:
        """Returns the index of the pixel at (x, y)."""
        return (
            int(self.width / self.scale * x + self.width / 2),
            int(self.width / self.scale * y + self.width / 2),
        )

    def update_ray(self, x: float, y: float, luminance: float, depth: float):
        """Updates the pixel at (x, y) with the given luminance."""
        if DEBUG:
            print("x: {}, y: {}".format(x, y))
        idx_x, idx_y = self.coord_to_idx(x, y)
        if DEBUG:
            print(f"idx_x: {idx_x}, idx_y: {idx_y}")
        if (idx_x < self.width) and (idx_y < self.width):
            if depth < self.depth_buffer[idx_x, idx_y]:
                if DEBUG:
                    print("ray crosses the screen, updating")
                self.depth_buffer[idx_x, idx_y] = depth
                self.pixels[idx_x, idx_y] = luminance
            elif DEBUG:
                print("ray does not cross the screen, not updating")

    def clear(self):
        """Clears the screen."""
        self.pixels = np.zeros((self.width, self.width))
        self.depth_buffer = np.full((self.width, self.width), np.inf)

    def display(self):
        """Displays the screen as ASCII art."""
        ascii_art = ""
        for row in np.rot90(self.pixels):
            ascii_art += (
                "".join([2 * luminance_to_char(luminance) for luminance in row])
            ) + "\n"
        return ascii_art


class Scene:
    def __init__(self, camera_distance: float, screen: Screen):
        self.meshes = []
        self.lights = []
        self.camera_distance = camera_distance
        self.screen = screen

    def add_mesh(self, mesh: Mesh, position: np.ndarray):
        self.meshes.append((position, mesh))

    def add_light(self, power: float, position: np.ndarray):
        self.lights.append((position, power))

    def render_mesh(self, mesh_idx=0):
        """Renders an object to the screen."""
        position, mesh = self.meshes[mesh_idx]
        max_lum = sum([light[1] for light in self.lights])
        distance = position[1]
        gain = self.camera_distance / (self.camera_distance + distance)

        # iterative update
        for i in range(len(mesh.vertices)):
            vertex, normal = mesh.vertices[i] + position, mesh.normals[i]
            x, depth, y = vertex
            if DEBUG:
                print(f"vertex: {vertex}, normal: {normal}")
            for light_pos, light_pow in self.lights:
                lum = compute_luminance(light_pos, light_pow, vertex, normal)
                assert lum >= 0, "ray reflected away"
                if DEBUG:
                    print(f"lum / max_lum: {lum / max_lum}")
                if lum > 0:  # beware, screen updated only for non null values
                    self.screen.update_ray(gain * x, gain * y, lum / max_lum, depth)

    def render(self):
        """Renders the scene to the screen."""
        for idx in range(len(self.meshes)):
            self.render_mesh(idx)


def normalize_vector(u):
    return u / np.linalg.norm(u)


def compute_luminance(light, light_power, vertice, normal):
    """Computes the luminance of a ray reflected on a surface in a specific direction."""
    u = normalize_vector(vertice - light)
    if np.dot(u, normal) <= 0:
        lum = light_power * (-np.dot(u, normal))
        assert lum >= 0, "luminance must be positive"
        return lum
    else:
        if DEBUG:
            print("light source behind the surface")
        return 0.0
