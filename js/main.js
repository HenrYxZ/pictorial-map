import * as THREE from 'https://cdn.skypack.dev/three@0.125';
import { OrbitControls } from 'https://cdn.skypack.dev/three@0.125/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://cdn.skypack.dev/three@0.125/examples/jsm/loaders/GLTFLoader.js';
import { Water } from 'https://cdn.skypack.dev/three@0.125/examples/jsm/objects/Water.js';

// Local Imports
import Placer from './placement.js';
import addSurface from './surface.js';


const gltfLoader = new GLTFLoader();
const SHADOW_MAP_SIZE = 8192;


async function asyncLoad(filepath) {
  return new Promise(
    (resolve, reject) => {
      gltfLoader.load(
        filepath, data => resolve(data), null, reject
      )
    }
  );
}

async function loadObject(assetObject) {
  const gltfData = await asyncLoad(assetObject.filepath);
  const newAsset = gltfData.scene;
  console.log("Loaded: " + assetObject.name);
  return newAsset;
}

async function loadAssets() {
  const assetsResponse = await fetch('../js/assets.json');
  const assetsJSON = await assetsResponse.json();
  const assets = [];
  for (let i = 0; i < assetsJSON.length; i++) {
    const newAsset = await loadObject(assetsJSON[i]);
    assets.push(newAsset);
  }
  return assets;
}

async function loadConfig(mapName) {
  const configResponse = await fetch('../assets/' + mapName + '/config.json');
  const config = await configResponse.json();
  return config;
}


export async function main(mapName, skyTexture) {
  const config = await loadConfig(mapName);
  const mapSize = config.mapSize;
  const canvas = document.querySelector('#c');
  const renderer = new THREE.WebGLRenderer({
    canvas, antialias: true, alpha: true
  });
  renderer.setPixelRatio( window.devicePixelRatio );
  renderer.setSize( window.innerWidth, window.innerHeight );
  // renderer.outputEncoding = THREE.LinearEncoding;
  renderer.outputEncoding = THREE.sRGBEncoding;
  // renderer.toneMapping = THREE.ACESFilmicToneMapping;
  // renderer.toneMappingExposure = 0.5;
  // renderer.toneMapping = THREE.NoToneMapping;
  renderer.shadowMap.enabled = true;
  // to antialias the shadow
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  // renderer.autoClear = false;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const camera = new THREE.PerspectiveCamera(30, width / height, 0.1, 10000);
  camera.position.z = mapSize;
  camera.position.x = mapSize;
  camera.position.y = mapSize;

  // Set Controls
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 0, 0);
  controls.update();

  // Set Scene
  const scene = new THREE.Scene();
  scene.background = skyTexture;

  // Add Surface
  await addSurface(mapName, scene);

  // Add directional light
  const color = 0xFFFFFF;
  const intensity = 1;
  const light = new THREE.DirectionalLight(color, intensity);
  light.castShadow = true;
  light.position.set(30, 100, -15);
  scene.add(light);
  scene.add(light.target);
  light.shadow.camera.left = -mapSize / 2;
  light.shadow.camera.right = mapSize;
  light.shadow.camera.bottom = -mapSize / 2;
  light.shadow.camera.top = mapSize / 2;
  light.shadow.camera.updateProjectionMatrix();
  // Change shadow map size
  light.shadow.mapSize.width = SHADOW_MAP_SIZE;
  light.shadow.mapSize.height = SHADOW_MAP_SIZE;

  // Add ambient light
  const ambient_light = new THREE.AmbientLight(0x78756d); // soft white light
  scene.add(ambient_light);

  // Add water
  const waterHeight = config.waterHeight;
  let water = null;
  if (waterHeight !== undefined) {
    const waterGeometry = new THREE.PlaneGeometry(mapSize, mapSize);
		water = new Water(
			waterGeometry,
			{
				textureWidth: 512,
				textureHeight: 512,
				waterNormals: new THREE.TextureLoader().load(
          '../assets/waternormals.jpg',
          function ( texture ) {
					  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
				  }
        ),
				sunDirection: new THREE.Vector3(),
				sunColor: 0xffffff,
				waterColor: 0x34cfeb,
				distortionScale: 1,
				fog: scene.fog !== undefined
			}
		);

		water.rotation.x = - Math.PI / 2;
    water.position.y = waterHeight;
		scene.add(water);
  }

  // Load assets
  const assets = await loadAssets();

  // Add scene objects from placement map
  const placer = new Placer(scene, assets);
  const placementResponse = await fetch(
    '../assets/' + mapName + '/placement.json'
  );
  const placement = await placementResponse.json();
  placer.usePlacement(placement);


  // Resize display
  function resizeRendererToDisplaySize(renderer) {
    const canvas = renderer.domElement;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const needResize = canvas.width !== width || canvas.height !== height;
    if (needResize) {
      renderer.setSize(width, height, false);
    }
    return needResize;
  }

  // Render function
  function render() {
    resizeRendererToDisplaySize(renderer)
    
    // animate water
    if (waterHeight !== undefined) {
      water.material.uniforms['time'].value += 1.0 / 60.0;
    }

    renderer.render(scene, camera);
    requestAnimationFrame(render);
  }

  // Hide loading message
  document.getElementById("spinner").hidden = true;

  requestAnimationFrame(render);
}

// -----------------------------------------------------------------------------
// Run the program

let url = window.location.href;
if (url.slice(-1) == "/") {
  url = url.substring(0, url.length - 1)
}
const mapName = url.split("/").pop();
const textureLoader = new THREE.TextureLoader();
textureLoader.load(
  '../assets/sky.png',
  texture => {
    texture.encoding = THREE.sRGBEncoding;
		texture.mapping = THREE.EquirectangularReflectionMapping;
    main(mapName, texture).catch(error => console.error(error));
  }
);
