#version 330

vec2 fragCoord = gl_FragCoord.xy;
uniform sampler2D iChannel0;
uniform vec3 iResolution;
uniform vec3 iResolutions[1];
uniform float t;
out vec4 fragColor;

#define PI 3.14

vec4 lerp(vec4 f0, vec4 f1, float x)
{
	vec4 fx = (1-x)*f0+x*f1;
	return fx;
}

vec4 bilerp(
	vec4 f00, vec4 f10, vec4 f01, vec4 f11,
	float x, float y)
{
	vec4 fx0 = lerp(f00,f10,x);
	vec4 fx1 = lerp(f01,f11,x);
	vec4 fxy = lerp(fx0,fx1,y);
	return fxy;
}

vec2 rot(vec2 p, float t)
{
	float c = cos(t);
	float s = sin(t);
	mat2 m = mat2(c,-s,s,c);
	return m*p;
}

void main()
{
	vec2 center = iResolution.xy/2;
	vec2 pt = fragCoord-center;
	pt = rot(pt,-t);
	pt += 0.5*iResolutions[0].xy;
	vec2 pts[4] = vec2[4](
		vec2(floor(pt.x),floor(pt.y)),
		vec2(ceil(pt.x),floor(pt.y)),
		vec2(floor(pt.x),ceil(pt.y)),
		vec2(ceil(pt.x),ceil(pt.y)));
	vec4 cols[4];
	for (int i = 0; i < 4; i++)
	{
		if (0 <= pts[i].x && pts[i].x < iResolutions[0].x
		&& 0 <= pts[i].y && pts[i].y < iResolutions[0].y)
		{
			vec2 uv = pts[i]/iResolutions[0].xy;
			cols[i] = texture(iChannel0,uv);
		}
		else
			cols[i] = vec4(0);
	}
	vec2 f = fract(pt);
	fragColor = bilerp(
		cols[0],cols[1],cols[2],cols[3],f.x,f.y);
}