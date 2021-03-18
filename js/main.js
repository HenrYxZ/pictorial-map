import * as THREE from 'https://threejsfundamentals.org/threejs/resources/threejs/r125/build/three.module.js';
import {OrbitControls} from 'https://threejsfundamentals.org/threejs/resources/threejs/r125/examples/jsm/controls/OrbitControls.js';
import {GLTFLoader} from 'https://threejsfundamentals.org/threejs/resources/threejs/r125/examples/jsm/loaders/GLTFLoader.js';
import {FBXLoader} from 'https://threejsfundamentals.org/threejs/resources/threejs/r125/examples/jsm/loaders/FBXLoader.js';

function main() {
  const canvas = document.querySelector('#c');
  const renderer = new THREE.WebGLRenderer({canvas, antialias: true});
  renderer.shadowMap.enabled = true;
  // to antialias the shadow
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;


  // Set Camera
  const size = 1;
  const near = 0.01;
  const far = 1000;
  const camera = new THREE.OrthographicCamera(
    -size, size, size, -size, near, far
  );
  camera.zoom = 0.1;
  camera.position.set(20, 20, 20);

  // Set Controls
  const controls = new OrbitControls(camera, canvas);
  controls.target.set(0, 0, 0);
  controls.update();

  // Set Scene
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('black');

  const textureLoader = new THREE.TextureLoader();

  // Add plane
  const planeSize = 40;
  const planeGeo = new THREE.PlaneBufferGeometry(planeSize, planeSize);
  const planeColor = 0xede1b4;
  const planeMat = new THREE.MeshPhongMaterial({
    color: planeColor,
    side: THREE.DoubleSide,
  });
  const plane = new THREE.Mesh(planeGeo, planeMat);
  plane.receiveShadow = true;
  plane.rotation.x = Math.PI * -.5;
  scene.add(plane);

  // Add directional light
  const color = 0xFFFFFF;
  const intensity = 1;
  const light = new THREE.DirectionalLight(color, intensity);
  light.castShadow = true;
  light.position.set(6, 20, -3);
  scene.add(light);
  scene.add(light.target);

  // Add ambient light
  const ambient_light = new THREE.AmbientLight(0x78756d); // soft white light
  scene.add(ambient_light);

  // Add test house
  const gltfLoader = new GLTFLoader();
  gltfLoader.load(
    'assets/square.glb',
    gltf => {
      const group = gltf.scene;
      group.traverse(
        child => { if (child.isMesh) child.castShadow = true; }
      );
      scene.add(group);
    }
  );

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
    camera.left   = -aspect;
    camera.right  =  aspect;
    camera.updateProjectionMatrix();

    scene.background.set(0x000000);
    renderer.render(scene, camera);

    requestAnimationFrame(render);
  }

  requestAnimationFrame(render);
}

main();
