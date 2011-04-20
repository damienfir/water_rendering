uniform mat4 worldcamera;
uniform mat4 modelworld;
uniform mat4 projection;

uniform mat3 modelworld_n;
uniform mat3 worldcamera_n;

uniform vec3 light;
uniform vec3 eye;

varying vec3 normal, lightVec, viewVec;

void main()
{
    vec3 vertex = vec3(modelworld * gl_Vertex);
	normal =  normalize(modelworld_n * gl_Normal);
	// normal = gl_Normal;
	
    // for texturing
    vec3 I = normalize(eye - vertex);
    vec3 reflectVec = normalize(reflect(I, normal));
    vec3 refractVec = normalize(refract(I, normal, 0.99));
    
    refractVec.y = -refractVec.y;
    
    gl_TexCoord[0].xyz = reflectVec;
    gl_TexCoord[1].xyz = refractVec;
    
    vertex = vec3(worldcamera * vec4(vertex, 1.0));
    normal = worldcamera_n * normal;
	
    // for phong lighting
	// vec3 light_cam = vec3(worldcamera * vec4(light, 1.0));
	lightVec = light - vertex;
	viewVec  = -vertex;
	
	gl_Position	= projection * vec4(vertex, 1.0);
}