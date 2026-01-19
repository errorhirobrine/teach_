from ursina import *

app = Ursina()
cube = Entity(model='cube', color=color.black, scale=2)

def update():
    cube.rotation_y += time.dt * 100  # Rotate the cube every frame
sfx = Audio('galaxy-meme.wav')
app.run()
    