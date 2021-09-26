import * as THREE from 'https://cdn.skypack.dev/three@0.125';
import {OrbitControls} from 'https://cdn.skypack.dev/three@0.125/examples/jsm/controls/OrbitControls.js';
import {GLTFLoader} from 'https://cdn.skypack.dev/three@0.125/examples/jsm/loaders/GLTFLoader.js';
// import {Water} from 'https://cdn.skypack.dev/three@0.125/examples/jsm/objects/Water.js';
import Placer from './placement.js';
import addSurface from './surface.js';

const gltfLoader = new GLTFLoader();
const MAP_WIDTH = 320;
const MAP_HEIGHT = 320;
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

/* async function loadConfig(mapName) {
  const configResponse = await fetch('../assets/' + mapName + '/config.json');
  const config = await configResponse.json();
  return config;
} */


export async function main(mapName, skyTexture) {
  const canvas = document.querySelector('#c');
  // const renderer = new THREE.WebGLRenderer({
  //   canvas, antialias: true
  // });
  const renderer = new THREE.WebGLRenderer({
    canvas, antialias: true, alpha: true
  });
  renderer.shadowMap.enabled = true;
  // to antialias the shadow
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.autoClear = false;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const aspectRatio = width / height;
  const skyCam = new THREE.PerspectiveCamera(30, width / height, 1000, 10000);
 //  const config = await loadConfig(mapName);

  // Set Camera
  const size = 150;
  const near = 0.00001;
  const far = 10000;
  const camera = new THREE.OrthographicCamera(
    -size * aspectRatio / 2,
    size * aspectRatio / 2,
    size / 2,
    -size / 2,
    near,
    far
  );
  camera.position.set(MAP_WIDTH, MAP_HEIGHT, MAP_HEIGHT);

  // Set Controls
  const controls = new OrbitControls(camera, canvas);
  controls.target.set(0, 0, 0);
  controls.update();

  // Set Scene
  const scene = new THREE.Scene();
  // scene.background = new THREE.Color('black');
  scene.background = null;
  const skyScene = new THREE.Scene();
  skyScene.background = skyTexture;
  // Add Sky Sphere
  // const skyMat = new THREE.MeshBasicMaterial({map: skyTexture});
  // skyMat.side = THREE.DoubleSide;
  // const skyGeo = new THREE.SphereGeometry(600, 60, 40);
  // const sky = new THREE.Mesh(skyGeo, skyMat);
  // scene.add(sky);

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
  light.shadow.camera.left = -MAP_WIDTH / 2;
  light.shadow.camera.right = MAP_WIDTH;
  light.shadow.camera.bottom = -MAP_HEIGHT / 2;
  light.shadow.camera.top = MAP_HEIGHT / 2;
  light.shadow.camera.updateProjectionMatrix();
  // Change shadow map size
  light.shadow.mapSize.width = SHADOW_MAP_SIZE;
  light.shadow.mapSize.height = SHADOW_MAP_SIZE;

  // Add ambient light
  const ambient_light = new THREE.AmbientLight(0x78756d); // soft white light
  scene.add(ambient_light);

/*   // Add water
  const waterHeight = config.waterHeight;
  let water = null;
  debugger;
  if (waterHeight !== undefined) {
    const waterGeometry = new THREE.PlaneGeometry(MAP_WIDTH, MAP_HEIGHT);
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
    debugger;
		scene.add(water);
  } */

  // Load assets
  const assets = await loadAssets();

  // Add scene objects from placement map
  const placer = new Placer(scene, assets);
  const placementResponse = await fetch(
    '../assets/' + mapName + '/placement.json'
  );
  const placement = await placementResponse.json();
  placer.usePlacement(placement);

  // Set Scissor
  function setScissorForElement(elem) {
    const canvasRect = canvas.getBoundingClientRect();
    const elemRect = elem.getBoundingClientRect();

    // compute a canvas relative rectangle
    const right = Math.min(elemRect.right, canvasRect.right) - canvasRect.left;
    const left = Math.max(0, elemRect.left - canvasRect.left);
    const bottom = Math.min(elemRect.bottom, canvasRect.bottom) - canvasRect.top;
    const top = Math.max(0, elemRect.top - canvasRect.top);

    const width = Math.min(canvasRect.width, right - left);
    const height = Math.min(canvasRect.height, bottom - top);

    // setup the scissor to only render to that part of the canvas
    const positiveYUpBottom = canvasRect.height - bottom;
    renderer.setScissor(left, positiveYUpBottom, width, height);
    renderer.setViewport(left, positiveYUpBottom, width, height);

    // return the aspect
    return width / height;
  }

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

    // turn on the scissor
    renderer.setScissorTest(true);

    const aspect = setScissorForElement(canvas);

    // update the camera for this aspect
    camera.left = -aspect * size / 2;
    camera.right = aspect * size / 2;
    camera.updateProjectionMatrix();

    /* // animate water
    if (waterHeight !== undefined) {
      water.material.uniforms['time'].value += 1.0 / 60.0;
    } */

    skyCam.position.copy(camera.position);
    skyCam.lookAt(0, 0, 0);

    renderer.clear();
    renderer.render(skyScene, skyCam);
    // renderer.render(scene, skyCam);
    renderer.render(scene, camera);

    requestAnimationFrame(render);
  }

  // Hide loading message
  document.getElementById("spinner").hidden = true;

  requestAnimationFrame(render);
}
