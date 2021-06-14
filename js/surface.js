import * as THREE from 'https://threejsfundamentals.org/threejs/resources/threejs/r125/build/three.module.js';

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


function getVerticesUVs(height, width, i, j) {
  //    |v2 |v1
  // ---|---|---           tr1 = v0, v1, v2
  //    |v0 |v3
  // ---|---|---           tr2 = v0, v3, v1
  //    |   |
  // It might be more efficient to use indices instead of repeating uvs
  const u = i / width;
  const v = (height - j) / height;
  const horizontalDiff = 1 / width;
  const verticalDiff = 1 / height;

  const u0 = u;
  const v0 = v - verticalDiff;

  const u1 = u + horizontalDiff;
  const v1 = v;

  const u2 = u;
  const v2 = v;

  const u3 = u1;
  const v3 = v0;

  return [[u0, v0], [u1, v1], [u2, v2], [u3, v3]];
}


function getTriangleUVs(verticesUVs) {
  //    |v2 |v1
  // ---|---|---           tr1 = v0, v1, v2
  //    |v0 |v3
  // ---|---|---           tr2 = v0, v3, v1
  //    |   |
  const [uv0, uv1, uv2, uv3] = verticesUVs;
  return [[uv0, uv1, uv2], [uv0, uv3, uv1]];
}


export default async function addSurface(mapName, scene) {
  const response = await fetch('../assets/' + mapName + '/surface.json');
  const surface = await response.json();
  const arrayList = [];
  const uvsList = [];
  const geom = new THREE.BufferGeometry();
  // Iterate in heightMap creating two triangles per pixel
  let v0, v1, v2, v3;
  let tr1, tr2;
  const {heightMap, maxHeight, pixelSize, height, width} = surface;
  for (let j = 0; j < height - 1; j++) {
    for (let i = 0; i < width - 1; i++) {
      [v0, v1, v2, v3] = createPoints(
        heightMap, i, j, maxHeight, pixelSize, height, width
      );
      const triangles = createTriangles(v0, v1, v2, v3);
      for (let triangle of triangles) {
        for (let point of triangle) {
          arrayList.push(...point);
        }
      }

      const verticesUVs = getVerticesUVs(height, width, i, j);
      const trianglesUVs = getTriangleUVs(verticesUVs);
      for (let triangleUVs of trianglesUVs) {
        for (let vertexUVs of triangleUVs) {
          uvsList.push(...vertexUVs);
        }
      }
    }
  }

  const vertices = new Float32Array(arrayList);
  geom.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
  const uvs = new Float32Array(uvsList);
  geom.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
  geom.computeVertexNormals();
  const textureLoader = new THREE.TextureLoader();
  const texture = textureLoader.load('../assets/' + mapName + '/surface.png');
  const material = new THREE.MeshPhongMaterial({
    map: texture, side: THREE.DoubleSide
  });
  const mesh = new THREE.Mesh(geom, material);
  mesh.receiveShadow = true;
  scene.add(mesh);
}
