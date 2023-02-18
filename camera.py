import glm
from math import cos, sin, radians
import pyglet
from pyglet.math import Mat4, Vec3, clamp
import weakref


class FPSCamera:
    def __init__(
        self, window,
        position=Vec3(0, 0, 0),
        target=Vec3(0, 0, -1),
        up=Vec3(0, 1, 0)
    ):
        self.position = position
        self.target = target
        self.up = up

        self.speed = 30

        # TODO: calculate these values from the passed Vectors
        self.pitch = 0
        # self.yaw = 2705
        self.yaw = 90

        self.input_map = {
            pyglet.window.key.W: "forward",
            pyglet.window.key.S: "backward",
            pyglet.window.key.A: "left",
            pyglet.window.key.D: "right",
        }

        self.forward = False
        self.backward = False
        self.left = False
        self.right = False

        self._window = weakref.proxy(window)
        self._window.view = Mat4.look_at(position, target, up)
        self._window.push_handlers(self)

    def on_resize(self, width, height):
        self._window.viewport = (0, 0, *self._window.get_framebuffer_size())
        self._window.projection = Mat4.perspective_projection(
            self._window.aspect_ratio, z_near=0.1, z_far=1000, fov=45
        )
        return pyglet.event.EVENT_HANDLED

    def on_refresh(self, dt):
        # Movement
        speed = self.speed * dt
        if self.forward:
            self.position += (self.target * speed)
        if self.backward:
            self.position -= (self.target * speed)
        if self.left:
            self.position -= (self.target.cross(self.up).normalize() * speed)
        if self.right:
            self.position += (self.target.cross(self.up).normalize() * speed)

        # Look

        # yaw = self.yaw * 0.1
        # pitch = self.pitch
        # self.target = Vec3(cos(radians(yaw)) * cos(radians(pitch)),
        #                    sin(radians(pitch)),
        #                    sin(radians(yaw)) * cos(radians(pitch))).normalize()
        phi = radians(self.yaw)
        theta = radians(self.pitch)
        self.target = Vec3(
            sin(theta) * cos(phi),
            cos(theta),
            sin(theta) * sin(phi)
        )

        eye = glm.vec3(*self.position)
        center = glm.vec3(*(self.position + self.target))
        up = glm.vec3(*self.up)

        l = []
        m = glm.lookAt(eye, center, up)
        for c in m:
            l.extend(c)

        self._window.view = tuple(l)

    # Mouse input

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, mod):
        self.yaw += dx
        self.pitch = clamp(self.pitch - dy, 0, 189.0)

    # Keyboard input

    def on_key_press(self, symbol, mod):
        if symbol in self.input_map:
            setattr(self, self.input_map[symbol], True)

    def on_key_release(self, symbol, mod):
        if symbol in self.input_map:
            setattr(self, self.input_map[symbol], False)
