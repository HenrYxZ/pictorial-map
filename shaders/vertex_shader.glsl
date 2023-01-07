#version 330


uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

uniform float uv_scale;
in vec3 position;
in vec2 tex_coords;

out vec3 v_vert;
out vec2 uv;

void main()
{
    uv = tex_coords * uv_scale;
    v_vert = position;
    gl_Position = window.projection * window.view * vec4(position, 1.0);
}