#version 330

vec2 fragCoord = gl_FragCoord.xy;
uniform vec2 c;
uniform vec2 b;

out float fragColor;

float sd_box(vec2 p, vec2 b)
{
	vec2 d = abs(p)-b;
	return length(max(d,0))+min(max(d.x,d.y),0);
}

void main()
{
	vec2 p = fragCoord-c;
	fragColor = sd_box(p,b);
}