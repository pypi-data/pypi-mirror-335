#version 330 core
layout (location = 0) in vec2 position;
layout (location = 1) in vec3 aColor;

out VS_OUT {
    vec3 color;
} vs_out;

void main() {
    vs_out.color = aColor;
    gl_Position = vec4(position, 0.0, 1.0);
}