import * as THREE from 'https://threejsfundamentals.org/threejs/resources/threejs/r125/build/three.module.js';
import {main} from './main.js';

const GROUND_COLOR = new THREE.Color('rgb(68, 115, 49)');
const mapName = 'shechem';

main(GROUND_COLOR, mapName).catch(error => console.error(error));
