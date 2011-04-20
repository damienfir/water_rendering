varying vec3 normal, lightVec, viewVec;

uniform samplerCube cubeEnv;

const float ambient = 0.3;
const float specularcontribution = 0.5;
const float diffusecontribution = 0.5;

void main()
{
    // ambient
    float lightIntensity = ambient;
    
    vec3 N = normalize(normal);
    vec3 L = normalize(lightVec);
    
    // diffuse
    float diffuse = dot(N, L);
	
	if (diffuse > 0.0) {
        lightIntensity += diffusecontribution * diffuse;
        
        // specular
        vec3 E = normalize(viewVec);
        vec3 R = normalize(reflect(-L, N));
        
		float spec = max(dot(R, E), 0.0);
		spec = pow(spec, 200.0);
		
        lightIntensity += specularcontribution * spec;
	}
	
    vec4 colorRefl = textureCube(cubeEnv, gl_TexCoord[0].xyz);
    vec4 colorRefr = textureCube(cubeEnv, gl_TexCoord[1].xyz);
	vec4 color = mix(colorRefl, colorRefr, 0.8);
	
	color = vec4(1,0,0,1);
	
    gl_FragColor = color * lightIntensity;
}