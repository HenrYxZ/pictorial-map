import pyglet
from pyglet.gl import *
from pyglet.graphics.shader import Shader, ShaderProgram
import numpy as np
from PIL import Image

DIFFUSE_MAP_UNIT = 0
NORMAL_MAP_UNIT = 1


class Terrain:
    def __init__(self, size=300, max_height=15, batch=None):
        """
        Object for a 3D terrain.
        Args:
            window (Window): The window that will display this terrain.
        """
        if not batch:
            self.batch = pyglet.graphics.Batch()
        self.size = size
        self.max_height = max_height
        self.diffuse_map = pyglet.resource.texture('assets/sf-sm/surface.png')
        self.normal_map = pyglet.resource.texture('assets/sf-sm/normal_map.png')

        # Create height map
        height_map_img = Image.open('assets/sf-sm/height_map.png').convert('L')
        self.height_map = np.asarray(height_map_img) / 255 * max_height
        # self.height_map = np.array([
        #     [1, 0.8, 0.6],
        #     [0.9, 0.5, 0.7],
        #     [0.3, 0.7, 0.6]
        # ])
        self.h, self.w = self.height_map.shape

        # Initialize vertices and indices
        self.vertices = self.init_vertices()
        self.indices = self.init_indices()
        self.tex_coords = self.init_tex_coords()

        # Read terrain shader program
        with open('shaders/vertex_shader.glsl', mode='r') as f:
            vs_str = f.read()
        vert_shader = Shader(vs_str, 'vertex')
        with open('shaders/fragment_shader.glsl', mode='r') as f:
            fs_str = f.read()
        frag_shader = Shader(fs_str, 'fragment')
        program = ShaderProgram(vert_shader, frag_shader)
        program['light_pos'] = (0.0, 200.0, -150.0)
        program['uv_scale'] = 3

        # Set render group
        render_group = RenderGroup(self.diffuse_map, self.normal_map, program)
        self.vertex_list = program.vertex_list_indexed(
            len(self.vertices), GL_TRIANGLE_STRIP, self.indices,
            batch=batch, group=render_group,
            position=('f', self.vertices),
            tex_coords=('f', self.tex_coords)
        )

    def init_vertices(self):
        vertices = []
        for j in range(self.h):
            for i in range(self.w):
                x = -self.size / 2 + (i / self.w) * self.size
                y = self.height_map[j, i]
                z = -(j / self.h) * self.size
                vertex = [x, y, z]
                vertices += vertex
        return vertices

    def init_tex_coords(self):
        tex_coords = []
        for j in range(self.h):
            for i in range(self.w):
                s = i / (self.w - 1)
                t = j / (self.h - 1)
                tex_coords += [s, t]
        return tex_coords

    def init_indices(self):
        indices = []
        for j in range(self.h - 2):
            for i in range(self.w):
                bottom_idx = j * self.w + i
                top_idx = (j + 1) * self.w + i
                # Maybe this could be reversed
                indices.append(bottom_idx)
                indices.append(top_idx)
            # Add last idx and next one to make an empty triangle
            last_idx = (j + 2) * self.w - 1
            next_idx = last_idx + 1
            indices.append(last_idx)
            indices.append(next_idx)
            indices.append(next_idx)
        # Do last row
        for i in range(self.w):
            bottom_idx = (self.h - 2) * self.w + i
            top_idx = (self.h - 1) * self.w + i
            indices.append(bottom_idx)
            indices.append(top_idx)
        return indices


class RenderGroup(pyglet.graphics.Group):
    def __init__(self, texture0, texture1, program):
        super().__init__()
        self.texture0 = texture0
        self.texture1 = texture1
        self.program = program

    def set_state(self):
        self.program.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(self.texture0.target, self.texture0.id)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(self.texture1.target, self.texture1.id)

    def unset_state(self):
        self.program.stop()
