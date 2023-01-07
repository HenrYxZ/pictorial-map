import pyglet
from pyglet.math import Mat4, Vec3


from camera import FPSCamera
from terrain import Terrain

batch = pyglet.graphics.Batch()


class Window(pyglet.window.Window):
    def __init__(self):
        super().__init__()
        # Create terrain
        self.terrain = Terrain(batch=batch)

    def on_draw(self):
        self.clear()
        batch.draw()

    def on_resize(self, width, height):
        self.viewport = (0, 0, *self.get_framebuffer_size())
        # Change window projection
        self.projection = Mat4.perspective_projection(
            self.aspect_ratio, z_near=0.1, z_far=255
        )
        return pyglet.event.EVENT_HANDLED


if __name__ == '__main__':
    window = Window()
    camera = FPSCamera(window, position=Vec3(0, 3, 5))
    pyglet.app.run()
