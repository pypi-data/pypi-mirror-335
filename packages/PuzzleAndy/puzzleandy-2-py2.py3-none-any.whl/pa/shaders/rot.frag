#version 330

vec2 fragCoord = gl_FragCoord.xy;
uniform sampler2D iChannel0;
uniform vec3 iResolution;
uniform vec3 iChannelResolution[1];
uniform float t;
out vec4 fragColor;

float w0(float a)
{
	return 1./6.*(-a*a*a+3.*a*a-3.*a+1);
}

float w1(float a)
{
	return 1./6.*(3.*a*a*a-6.*a*a+4.);
}

float w2(float a)
{
	return 1./6.*(-3.*a*a*a+3.*a*a+3.*a+1.);
}

float w3(float a)
{
	return 1./6.*a*a*a;
}

float g0(float a)
{
	return w0(a)+w1(a);
}

float g1(float a)
{
	return w2(a)+w3(a);
}

float h0(float a)
{
	return 1.-w1(a)/(w0(a)+w1(a))+a;
}

float h1(float a)
{
	return 1.+w3(a)/(w2(a)+w3(a))-a;
}

vec4 texture_bicubic(vec2 uv)
{
	vec2 px = uv*iChannelResolution[0].xy+0.5;

	vec2 ipx = floor(px);
	vec2 fpx = fract(px);

	float g0x = g0(fpx.x);
	float g1x = g1(fpx.x);
	float g0y = g0(fpx.y);
	float g1y = g1(fpx.y);
	float h0x = h0(fpx.x);
	float h1x = h1(fpx.x);
	float h0y = h0(fpx.y);
	float h1y = h1(fpx.y);

	vec2 px0 = vec2(ipx.x+(fpx.x-h0x),ipx.y+(fpx.y-h0y));
	vec2 px1 = vec2(ipx.x+(fpx.x+h1x),ipx.y+(fpx.y-h0y));
	vec2 px2 = vec2(ipx.x+(fpx.x-h0x),ipx.y+(fpx.y+h1y));
	vec2 px3 = vec2(ipx.x+(fpx.x+h1x),ipx.y+(fpx.y+h1y));

	vec2 uv0 = (px0-0.5)/iChannelResolution[0].xy;
	vec2 uv1 = (px1-0.5)/iChannelResolution[0].xy;
	vec2 uv2 = (px2-0.5)/iChannelResolution[0].xy;
	vec2 uv3 = (px3-0.5)/iChannelResolution[0].xy;

	vec4 col0 = texture(iChannel0,uv0);
	vec4 col1 = texture(iChannel0,uv1);
	vec4 col2 = texture(iChannel0,uv2);
	vec4 col3 = texture(iChannel0,uv3);

	return
		g0y*(g0x*col0+g1x*col1)+
		g1y*(g0x*col2+g1x*col3);
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
	vec2 px = fragCoord;
	px -= iResolution.xy/2;
	px = rot(px,-t);
	vec2 uv = px/iChannelResolution[0].xy;
	uv += 0.5;
	fragColor = texture_bicubic(uv);
}