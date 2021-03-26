import * as THREE from 'https://threejsfundamentals.org/threejs/resources/threejs/r125/build/three.module.js';
import {GLTFLoader} from 'https://threejsfundamentals.org/threejs/resources/threejs/r125/examples/jsm/loaders/GLTFLoader.js';
const RBGA_CHANNELS = 4;


export class Placer {
  constructor(scene, assets) {
    this.scene = scene;
    this.assets = assets;
  }

  placeObject(sceneObject, asset) {
    const newObject = asset.clone();
    // Move to transform
    const position = sceneObject.position;
    newObject.position.set(position.x, position.y, position.z);
    newObject.rotation.y = sceneObject.rotation;
    const scale = sceneObject.scale;
    newObject.scale.set(scale.x, scale.y, scale.z);
    // Add shadows
    newObject.traverse(
      child => {
        if (child.isMesh) {
          child.castShadow = true;
        }
      }
    );
    // Add to scene
    this.scene.add(newObject);
    console.log("Placed object with id: " + sceneObject.assetId)
  }

  usePlacement(placement) {
    placement.forEach(
      item => {
        const asset = this.assets[item.assetId - 1];
        this.placeObject(item, asset);
      }
    );
  }

  // loadSquareHouse() {
  //   loadObject(
  //     "square house", 'assets/square.glb', child => this.squareHouse = child
  //   );
  // }

  // Read a black and white image and place in the map where the pixel is white
  // procedurallyPlace(placementMap, rows, columns) {
  //   const Z_POSITION = 0;
  //   const footprint = 5;
  //   for (let j = 0; j < rows; j++) {
  //     for (let i = 0; i < columns; i++) {
  //       // Only get red channel value
  //       let pixelValue = placementMap.getImageData(i, j, 1, 1)[0];
  //       if (pixelValue > 0) {
  //         let newHouse = this.squareHouse.clone();
  //         let x = (i - rows / 2) * footprint;
  //         let y = (j - columns / 2) * footprint;
  //         newHouse.position.set(x, y, Z_POSITION);
  //         this.scene.add(newHouse);
  //       }
  //     }
  //   }
  // }
}
