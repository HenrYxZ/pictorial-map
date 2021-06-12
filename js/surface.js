import * as THREE from 'https://threejsfundamentals.org/threejs/resources/threejs/r125/build/three.module.js';
const GROUND_COLOR = new THREE.Color('rgb(161, 153, 95)');
const MAX_COLOR = 255;


function createPoints(heightMap, i, j, maxHeight, pixelSize, height, width) {
  //    |v2 |v1
  // ---|---|---           tr1 = v0, v1, v2
  //    |v0 |v3
  // ---|---|---           tr2 = v0, v3, v1
  //    |   |
  const x0 = (i - width / 2) * pixelSize;
  const z0 = (j + 1 - height / 2) * pixelSize;
  const y0 = (heightMap[j + 1][i] / MAX_COLOR) * maxHeight;

  const x1 = x0 + pixelSize;
  const z1 = z0 - pixelSize;
  const y1 = (heightMap[j][i + 1] / MAX_COLOR) * maxHeight;

  const x2 = x0;
  const z2 = z0 - pixelSize;
  const y2 = (heightMap[j][i] / MAX_COLOR) * maxHeight;

  const x3 = x1;
  const z3 = z0;
  const y3 = (heightMap[j + 1][i + 1] / MAX_COLOR) * maxHeight;

  return [[x0, y0, z0], [x1, y1, z1], [x2, y2, z2], [x3, y3, z3]];
}

function createTriangles(v0, v1, v2, v3) {
  //    |v2 |v1
  // ---|---|---           tr1 = v0, v1, v2
  //    |v0 |v3
  // ---|---|---           tr2 = v0, v3, v1
  //    |   |
  const tr1 = [v0, v1, v2];
  const tr2 = [v0, v3, v1];
  return [tr1, tr2];
}

export default async function addSurface(mapName, scene) {
  const response = await fetch('../assets/' + mapName + '/surface.json');
  const surface = await response.json();
  const arrayList = [];
  const geom = new THREE.BufferGeometry();
  // Iterate in heightMap creating two triangles per pixel
  let v0, v1, v2, v3;
  let tr1, tr2;
  const {heightMap, surfaceTex, maxHeight, pixelSize, height, width} = surface;
  debugger;
  for (let j = 0; j < height - 1; j++) {
    for (let i = 0; i < width - 1; i++) {
      [v0, v1, v2, v3] = createPoints(
        heightMap, i, j, maxHeight, pixelSize, height, width
      );
      const triangles = createTriangles(v0, v1, v2, v3);
      for (let triangle of triangles) {
        for (let point of triangle) {
          for (let vertex of point) {
            arrayList.push(vertex);
          }
        }
      }
    }
  }

  const vertices = new Float32Array(arrayList);
  geom.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
  geom.computeVertexNormals();
  const material = new THREE.MeshPhongMaterial({
    color: GROUND_COLOR,
    side: THREE.DoubleSide
  });
  const mesh = new THREE.Mesh(geom, material);
  mesh.receiveShadow = true;
  scene.add(mesh);
}
