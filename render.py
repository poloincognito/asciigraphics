from donut import *
from utils import *
import pickle

### Spinning donut ###
frames = []
# screen
num_pixels, scale_screen = 40, 1.0
screen = Screen(num_pixels, scale_screen)
# donut
vertices, normals = generate_donut_mesh(0.5, 0.25, scale_screen, num_pixels)
donut = RotatableMesh(vertices, normals)
# scene
camera_distance = 1.0  # camera distance
new_scene = Scene(camera_distance, screen)
new_scene.add_mesh(donut, np.array([0.0, 1.5, 0.0]))
new_scene.add_light(1.0, np.array([0.0, -5.0, 3.0]))  # light intensity, light position
for i in range(20):
    new_scene.screen.clear()
    donut.rotate(-0.05 * np.pi, "z")
    new_scene.render()
    frames.append(new_scene.screen.display())
print("Rendering done!")

with open("frames.pkl", "wb") as file:
    pickle.dump(frames, file)
