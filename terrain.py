import pyglet
from pyglet.gl import *
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.graphics import ShaderGroup
from pyglet.math import Vec2, Vec3


DEBUG_NORMALS = "normals"


class RenderGroup(pyglet.graphics.Group):
    def __init__(self, texture0, program):
        super().__init__()
        self.texture0 = texture0
        self.program = program

    def set_state(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(self.texture0.target, self.texture0.id)
        glEnable(GL_DEPTH_TEST)
        self.program.use()

    def unset_state(self):
        self.program.stop()


class Vertex:
    def __init__(self, position=Vec3(), normal=Vec3(), uv=Vec2()):
        self.position = position
        self.normal = normal
        self.uv = uv


class Terrain:
    def __init__(
        self, size, max_height, height_map, diffuse_map, batch=None
    ):
        """
        Object for a 3D terrain.
        """
        if not batch:
            self.batch = pyglet.graphics.Batch()
        self.debug_normals_batch = pyglet.graphics.Batch()
        self.current_debug_mode = DEBUG_NORMALS
        self.size = size
        self.max_height = max_height
        self.height_map = height_map

        # Create height map
        self.h, self.w = self.height_map.shape

        # Initialize vertices and indices
        self.vertices = []
        self.positions, self.tex_coords = self.init_vertices()
        self.indices = self.init_indices()
        self.normals = self.calculate_normals()
        self._is_in_debug_mode = False

        # Read terrain shader program
        with open('shaders/vertex_shader.glsl', mode='r') as f:
            vs_str = f.read()
        vert_shader = Shader(vs_str, 'vertex')

        with open('shaders/fragment_shader.glsl', mode='r') as f:
            fs_str = f.read()
        frag_shader = Shader(fs_str, 'fragment')

        with open('shaders/normals.glsl', mode='r') as f:
            normals_fs_str = f.read()
        normals_frag_shader = Shader(normals_fs_str, 'fragment')

        program = ShaderProgram(vert_shader, frag_shader)
        program['light_pos'] = (0.0, 200.0, -150.0)
        program['uv_scale'] = 1

        # Set render group
        self.render_group = RenderGroup(diffuse_map, program)
        self.vertex_list = program.vertex_list_indexed(
            len(self.vertices), GL_TRIANGLE_STRIP, self.indices,
            batch=batch, group=self.render_group,
            position=('f', self.positions),
            tex_coords=('f', self.tex_coords),
            normal=('f', self.normals)
        )

        debug_normals_program = ShaderProgram(vert_shader, normals_frag_shader)
        self.normals_group = ShaderGroup(debug_normals_program)
        self.normals_vli = debug_normals_program.vertex_list_indexed(
            len(self.vertices), GL_TRIANGLE_STRIP, self.indices,
            batch=batch, group=self.normals_group,
            position=('f', self.positions),
            normal=('f', self.normals)
        )

    @property
    def is_in_debug_mode(self):
        return self._is_in_debug_mode

    @is_in_debug_mode.setter
    def is_in_debug_mode(self, value):
        if self.current_debug_mode == DEBUG_NORMALS:
            self.normals_group.visible = value
        else:
            self.normals_group.visible = False
        self.render_group.visible = not value
        self._is_in_debug_mode = value

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
        last_idx = self.h * self.w - 1
        for _ in range(3):
            indices.append(last_idx)
        return indices

    def calculate_normals(self):
        # Go row by row
        vertices_per_row = 2 * self.w + 3
        for j in range(self.h):
            for i in range(0, vertices_per_row - 4, 4):
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
