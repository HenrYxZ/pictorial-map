import pyglet
from pyglet.gl import *
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.math import Vec2, Vec3
import numpy as np
from PIL import Image


class Vertex:
    def __init__(self, position=Vec3(), normal=Vec3(), uv=Vec2()):
        self.position = position
        self.normal = normal
        self.uv = uv


class Terrain:
    def __init__(self, size=300, max_height=30, batch=None):
        """
        Object for a 3D terrain.
        """
        if not batch:
            self.batch = pyglet.graphics.Batch()
        self.size = size
        self.max_height = max_height
        self.diffuse_map = pyglet.resource.texture('assets/sf-sm/surface.png')

        # Create height map
        height_map_img = Image.open('assets/sf-sm/height_map.png').convert('L')
        self.height_map = np.asarray(height_map_img) / 255 * max_height
        self.h, self.w = self.height_map.shape

        # Initialize vertices and indices
        self.vertices = []
        self.positions, self.tex_coords = self.init_vertices()
        self.indices = self.init_indices()
        self.normals = self.calculate_normals()

        # Read terrain shader program
        with open('shaders/vertex_shader.glsl', mode='r') as f:
            vs_str = f.read()
        vert_shader = Shader(vs_str, 'vertex')
        with open('shaders/fragment_shader.glsl', mode='r') as f:
            fs_str = f.read()
        frag_shader = Shader(fs_str, 'fragment')
        program = ShaderProgram(vert_shader, frag_shader)
        program['light_pos'] = (0.0, 200.0, -150.0)
        program['uv_scale'] = 1

        # Set render group
        # render_group = RenderGroup(self.diffuse_map, self.normal_map, program)
        render_group = RenderGroup(self.diffuse_map, program)
        self.vertex_list = program.vertex_list_indexed(
            len(self.vertices), GL_TRIANGLE_STRIP, self.indices,
            batch=batch, group=render_group,
            position=('f', self.positions),
            tex_coords=('f', self.tex_coords),
            normal=('f', self.normals)
        )

    def init_vertices(self):
        positions = []
        tex_coords = []
        for j in range(self.h):
            for i in range(self.w):
                x = -self.size / 2 + (i / self.w) * self.size
                y = self.height_map[j, i]
                z = -(j / self.h) * self.size
                pos = [x, y, z]
                positions += pos

                s = i / (self.w - 1)
                t = j / (self.h - 1)
                tex_coords += [s, t]

                self.vertices.append(
                    Vertex(position=Vec3(x, y, z), uv=Vec2(s, t))
                )
        return positions, tex_coords

    def init_indices(self):
        indices = []
        for j in range(self.h - 1):
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

    def calculate_normals(self):
        # Go row by row
        vertices_per_row = 2 * self.w + 3
        for j in range(self.h):
            for i in range(0, self.w - 4, 2):
                offset = j * vertices_per_row
                idx0 = self.indices[i + offset]
                idx1 = self.indices[i + 1 + offset]
                idx2 = self.indices[i + 2 + offset]
                idx3 = self.indices[i + 3 + offset]

                v0 = self.vertices[idx2].position - self.vertices[idx0].position
                v1 = self.vertices[idx1].position - self.vertices[idx0].position
                normal = v0.cross(v1)
                normal = normal.normalize()

                # Add normal contribution of each triangle normal a vertex
                # belongs to
                self.vertices[idx0].normal += normal
                self.vertices[idx1].normal += normal
                self.vertices[idx2].normal += normal

                v0 = self.vertices[idx3].position - self.vertices[idx2].position
                v1 = self.vertices[idx1].position - self.vertices[idx2].position
                normal = v0.cross(v1)
                normal = normal.normalize()

                self.vertices[idx1].normal += normal
                self.vertices[idx2].normal += normal
                self.vertices[idx3].normal += normal

        # Normalize every normal
        normals = []
        for v in self.vertices:
            normal = v.normal.normalize()
            normals += [normal.x, normal.y, normal.z]
        return normals


class RenderGroup(pyglet.graphics.Group):
    # def __init__(self, texture0, texture1, program):
    def __init__(self, texture0, program):
        super().__init__()
        self.texture0 = texture0
        # self.texture1 = texture1
        self.program = program

    def set_state(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(self.texture0.target, self.texture0.id)
        # glActiveTexture(GL_TEXTURE1)
        # glBindTexture(self.texture1.target, self.texture1.id)
        glEnable(GL_DEPTH_TEST)
        self.program.use()

    def unset_state(self):
        self.program.stop()
