const FULL_ROTATION = "full";


export default class Placer {
  constructor(scene, assets) {
    this.scene = scene;
    this.assets = assets;
  }

  placeObject(sceneObject, asset) {
    const newObject = asset.clone();
    // Move to transform
    const position = sceneObject.position;
    newObject.position.set(position.x, position.y, position.z);
    if (sceneObject.rotation == FULL_ROTATION) {
      newObject.rotation.x = Math.random() * 2 *  Math.PI;
      newObject.rotation.y = Math.random() * 2 * Math.PI;
      newObject.rotation.z = Math.random() * 2 * Math.PI;
    } else {
      newObject.rotation.y = sceneObject.rotation;
    }
    const scale = sceneObject.scale;
    newObject.scale.set(scale.x, scale.y, scale.z);
    // Add shadows
    newObject.traverse(
      child => {
        if (child.isMesh) {
          child.castShadow = true;
          // const randomColorChange = Math.random() * MAX_COLOR_CHANGE;
          // child.material.color.multiplyScalar(1 - randomColorChange);
          // child.material.needsUpdate = true;
        }
      }
    );
    // Add to scene
    this.scene.add(newObject);
    // console.log("Placed object with id: " + sceneObject.assetId)
  }

  usePlacement(placement) {
    placement.forEach(
      item => {
        const asset = this.assets[item.assetId - 1];
        this.placeObject(item, asset);
      }
    );
  }
}
