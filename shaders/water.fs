varying vec3 normal, lightVec, viewVec;

uniform samplerCube cubeEnv;

const float ambient = 0.5;
const float specularcontribution = 0.5;
const float diffusecontribution = 0.7;

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
		spec = pow(spec, 100.0);
		
        lightIntensity += specularcontribution * spec;
	}
	
    vec4 colorRefl = textureCube(cubeEnv, gl_TexCoord[0].xyz);
    
    vec4 colorRefr = textureCube(cubeEnv, gl_TexCoord[1].xyz);
	
    gl_FragColor = mix(colorRefl, colorRefr, 0.4) * lightIntensity;
}