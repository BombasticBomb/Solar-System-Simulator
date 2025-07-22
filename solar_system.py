from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
import numpy as np

app = Ursina(bgcolor=color.black)

# ------------------ Simulation Control Variables ------------------
simulation_speed = 5
simulation_paused = False
zoom_speed = 10  # <-- Adjust zoom speed here

# ------------------ Load Textures ------------------
SunIMG = load_texture("sun.png", filtering=None)
MercuryIMG = load_texture("mercury.png", filtering=None)
VenusIMG = load_texture("venus.jpg", filtering=None)
EarthIMG = load_texture("earth.jpg", filtering=None)
MarsIMG = load_texture("mars.jpg", filtering=None)
JupiterIMG = load_texture("jupiter.jpg", filtering=None)
SaturnIMG = load_texture("saturn.jpg", filtering=None)
UranusIMG = load_texture("uranus.png", filtering=None)
NeptuneIMG = load_texture("neptune.jpg", filtering=None)
background_texture = load_texture("background.jpg")
ring_texture = load_texture("circle")  # Transparent ring texture (optional)

# ------------------ Create 360° Space Background ------------------
sky = Entity(
    model='sphere',
    scale=1000,
    texture=background_texture,
    double_sided=True,
    collider=None
)

sun = Entity(model="sphere", scale=5, texture=SunIMG)

# ------------------ Create Planet Entities ------------------
planets = {
    'mercury': Entity(model="sphere", scale=0.1, texture=MercuryIMG),
    'venus':   Entity(model="sphere", scale=0.3, texture=VenusIMG),
    'earth':   Entity(model="sphere", scale=0.35, texture=EarthIMG),
    'mars':    Entity(model="sphere", scale=0.15, texture=MarsIMG),
    'jupiter': Entity(model="sphere", scale=0.9, texture=JupiterIMG),
    'saturn':  Entity(model="sphere", scale=0.6, texture=SaturnIMG),
    'uranus':  Entity(model="sphere", scale=0.5, texture=UranusIMG),
    'neptune': Entity(model="sphere", scale=0.45, texture=NeptuneIMG),
}

# ------------------ Create Planet Rings ------------------
def create_ring(parent, scale=(1, 1), texture='white_circle', color=color.white33, y_offset=0.05):
    return Entity(
        parent=parent,
        model='quad',
        scale=scale,
        texture=texture,
        color=color,
        rotation_x=90,
        y=y_offset,
        double_sided=True
    )

# Adjust the rings: smaller and greyish
create_ring(planets['saturn'], scale=(1.8, 1.8), texture=ring_texture, color=color.rgba(150, 150, 150, 160), y_offset=0.05)
create_ring(planets['jupiter'], scale=(1.1, 1.1), texture=ring_texture, color=color.rgba(140, 140, 140, 60), y_offset=0.04)
create_ring(planets['uranus'], scale=(1.4, 1.4), texture=ring_texture, color=color.rgba(130, 180, 230, 50), y_offset=0.045)
create_ring(planets['neptune'], scale=(1.2, 1.2), texture=ring_texture, color=color.rgba(80, 130, 230, 40), y_offset=0.04)

# ------------------ Orbital Setup ------------------
orbit_radius = {
    'mercury': 6, 'venus': 8, 'earth': 10, 'mars': 12,
    'jupiter': 15, 'saturn': 18, 'uranus': 21, 'neptune': 24,
}
orbit_speed = {
    'mercury': 1.6, 'venus': 1.2, 'earth': 1, 'mars': 0.8,
    'jupiter': 0.6, 'saturn': 0.5, 'uranus': 0.4, 'neptune': 0.3,
}
angles = {name: 0 for name in planets}

# ------------------ Planet Self-Rotation ------------------
planet_rotation_speed = {
    'mercury': 60,
    'venus': 70,
    'earth': 65,
    'mars': 70,
    'jupiter': 150,
    'saturn': 100,
    'uranus': 80,
    'neptune': 80,
}

# ------------------ Camera Animation Setup ------------------
animation_state = 0
animation_timer = 0
earth_orbit_angle = 0
earth_orbit_radius = 2
earth_orbit_speed = 2
top_view_height = 50
top_view_angle = (90, 0, 0)
return_distance = -40
return_rotation = (0, 0, 0)
animation_duration_to_earth = 5
animation_duration_earth_orbit = 10
animation_duration_out = 5
animation_duration_top_view = 5
animation_duration_return = 5

original_camera_position = camera.position
original_camera_rotation = camera.rotation
target_position = Vec3(0, 0, 0)
target_rotation = Vec3(0, 0, 0)
animation_running = True
editor_camera_activated = False

# ------------------ Update Function ------------------
def update():
	# Restart
    if held_keys['escape']:
        os.execv(sys.executable, ['python'] + sys.argv)
	
    global animation_state, animation_timer, original_camera_position, original_camera_rotation
    global earth_orbit_angle, target_position, target_rotation, animation_running, editor_camera_activated
    global simulation_speed, simulation_paused

    if not simulation_paused:
        sun.rotation_y += time.dt * 10 * simulation_speed
        sky.rotation_y += time.dt * 0.1 * simulation_speed

        for name, planet in planets.items():
            angles[name] += time.dt * orbit_speed[name] * simulation_speed
            r = orbit_radius[name]
            planet.x = r * np.cos(angles[name])
            planet.z = r * np.sin(angles[name])
            planet.rotation_y += time.dt * planet_rotation_speed[name] * simulation_speed

        if animation_running:
            animation_timer += time.dt * simulation_speed

            if animation_state == 0:
                if animation_timer >= 2:
                    animation_state = 1
                    animation_timer = 0
                    original_camera_position = camera.position
                    original_camera_rotation = camera.rotation
                    target_position = planets['earth'].position + Vec3(0, 1, -20)
                    target_rotation = (10, 0, 0)

            elif animation_state == 1:
                progress = min(1, animation_timer / animation_duration_to_earth)
                camera.position = lerp(original_camera_position, target_position, progress)
                camera.rotation = lerp(original_camera_rotation, target_rotation, progress)
                if progress >= 1:
                    animation_state = 2
                    animation_timer = 0
                    earth_orbit_angle = 0

            elif animation_state == 2:
                earth_orbit_angle += time.dt * earth_orbit_speed * simulation_speed
                camera.position = planets['earth'].position + Vec3(
                    earth_orbit_radius * np.cos(earth_orbit_angle),
                    earth_orbit_radius * np.sin(earth_orbit_angle),
                    -10
                )
                camera.look_at(planets['earth'])
                if animation_timer >= animation_duration_earth_orbit:
                    animation_state = 3
                    animation_timer = 0
                    original_camera_position = camera.position
                    original_camera_rotation = camera.rotation
                    target_position = camera.position + Vec3(0, 10, -30)
                    target_rotation = (30, 0, 0)

            elif animation_state == 3:
                progress = min(1, animation_timer / animation_duration_out)
                camera.position = lerp(original_camera_position, target_position, progress)
                camera.rotation = lerp(original_camera_rotation, target_rotation, progress)
                if progress >= 1:
                    animation_state = 4
                    animation_timer = 0
                    original_camera_position = camera.position
                    original_camera_rotation = camera.rotation

            elif animation_state == 4:
                progress = min(1, animation_timer / animation_duration_top_view)
                camera.position = lerp(original_camera_position, Vec3(0, top_view_height, 0), progress)
                camera.rotation = lerp(original_camera_rotation, top_view_angle, progress)
                if progress >= 1:
                    animation_state = 5
                    animation_timer = 0
                    original_camera_position = camera.position
                    original_camera_rotation = camera.rotation

            elif animation_state == 5:
                progress = min(1, animation_timer / animation_duration_return)
                camera.position = lerp(original_camera_position, Vec3(0, 0, return_distance), progress)
                camera.rotation = lerp(original_camera_rotation, return_rotation, progress)
                if progress >= 1:
                    animation_running = False

    if not animation_running and not editor_camera_activated:
        ec = EditorCamera()
        ec._drag_button = 'left'
        editor_camera_activated = True

# ------------------ Input Function ------------------
def input(key):
    global simulation_speed, simulation_paused
    if key == 'space':
        simulation_paused = not simulation_paused
        print("Simulation Paused" if simulation_paused else "Simulation Running")
    elif key == 'up arrow':
        simulation_speed *= 1.2
        print("Simulation speed increased to:", simulation_speed)
    elif key == 'down arrow':
        simulation_speed /= 1.2
        print("Simulation speed decreased to:", simulation_speed)
    elif key == 'scroll up':
        camera.z += time.dt * zoom_speed
    elif key == 'scroll down':
        camera.z -= time.dt * zoom_speed

camera.z = -40
app.run()
