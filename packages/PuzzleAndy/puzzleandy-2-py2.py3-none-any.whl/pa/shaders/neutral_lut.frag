#version 330

vec2 fragCoord = gl_FragCoord.xy;
uniform int n;

out vec3 fragColor;

int quot(int x, int y)
{
	return int(floor(x/y));
}

void main()
{
	int x = int(fragCoord.x);
	int y = int(fragCoord.y);
	vec3 c;
	c.r = mod(x,n)/(n-1);
	c.g = mod(y,n)/(n-1);
	int slice_row = quot(y,n);
	int slice_col = quot(x,n);
	c.b = (slice_row*sqrt(n)+slice_col)/n;
	fragColor = vec3(c);
}