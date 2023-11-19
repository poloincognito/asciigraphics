import time
import sys
import pickle

with open("frames.pkl", "rb") as file:
    frames = pickle.load(file)


def animation(timestep: int) -> str:
    """Returns a character from the animation string based on the timestep."""
    return frames[timestep % len(frames)]


# animation parameters
duration = 10  # The animation will last for 10 seconds
timestep = 0.1

# animation loop
start_time = time.time()
i = 0
while True:
    i += 1
    time.sleep(timestep)  # Feel free to experiment with the speed here
    sys.stdout.write("\r" + animation(i))
    sys.stdout.flush()
    if time.time() - start_time > duration:
        break
