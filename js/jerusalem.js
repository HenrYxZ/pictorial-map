import * as THREE from 'https://threejsfundamentals.org/threejs/resources/threejs/r125/build/three.module.js';
import {main} from './main.js';

const mapName = 'jerusalem';
// Add Sky
const textureLoader = new THREE.TextureLoader();
const texture = textureLoader.load(
  '../assets/sky.png',
  texture => {
    texture.encoding = THREE.sRGBEncoding;
		texture.mapping = THREE.EquirectangularReflectionMapping;
    main(mapName, texture).catch(error => console.error(error));
  }
);
