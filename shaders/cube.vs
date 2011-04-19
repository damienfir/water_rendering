uniform mat4 modelworld;
uniform mat4 worldcamera;
uniform mat4 projection;

uniform vec3 eyeposition;

void main()
{	  
    vec3 vertex = vec3(modelworld * gl_Vertex);
	
	gl_TexCoord[0].xyz = normalize(eyeposition - vertex);
	
	gl_Position = projection * worldcamera * vec4(vertex, 1.0);
}