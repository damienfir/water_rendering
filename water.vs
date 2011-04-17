uniform mat4 modelworld;
uniform mat4 worldcamera;
uniform mat4 projection;

void main()
{
	gl_Position = projection * worldcamera * modelworld * gl_Vertex;
}