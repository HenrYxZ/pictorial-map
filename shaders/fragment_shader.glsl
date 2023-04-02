#version 330


uniform sampler2D image;
uniform vec3 light_pos;
in vec2 uv;
in vec3 v_vert;
in vec3 n;

out vec4 f_color;

void main() {
    vec3 l = normalize(light_pos - v_vert);
    float n_dot_l = clamp(dot(l, n), 0.0, 1.0);
    float ambient = 0.2;
    vec3 diffuse = texture(image, uv).rgb;
    vec3 color = clamp(diffuse * (n_dot_l + ambient), 0.0, 1.0);
    f_color = vec4(color, 1.0);
}
