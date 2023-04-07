#version 330

in vec2 uv;
in vec3 v_vert;
in vec3 n;

out vec4 f_color;

void main() {
    f_color = vec4(n / 2.0 + 0.5, 0.0);
}
