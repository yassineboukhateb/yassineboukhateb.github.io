// Usage: node project.mjs SOURCE_DIRECTORY OUTPUT_JSON
import { writeFile } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

const [sourceDirectory, outputFile] = process.argv.slice(2);
if (!sourceDirectory || !outputFile) throw new Error('Provide the original animation directory and an output JSON path.');
const source = resolve(sourceDirectory);
const THREE = await import(pathToFileURL(join(source, 'vendor/three.module.min.js')).href);
const { simulate, slerp, distance, CENTER, TOTAL, RADIUS, A } = await import(pathToFileURL(join(source, 'math.mjs')).href);
const data = simulate(24817);
const camera = new THREE.OrthographicCamera(-1.28, 1.28, 1.28 * 148 / 228, -1.28 * 148 / 228, 0.01, 50);
camera.position.set(2.8, 2.6, 4.5);
camera.lookAt(0, 0.25, 0);
camera.updateProjectionMatrix();
camera.updateMatrixWorld(true);

const project = (point, scale = 1) => {
  const vector = new THREE.Vector3(...point.map(value => value * scale)).project(camera);
  return [vector.x, vector.y];
};
const grid = [];
for (let j = 1; j <= 3; j++) {
  const theta = Math.PI * j / 8;
  grid.push(Array.from({ length: 129 }, (_, i) => {
    const phi = i * 2 * Math.PI / 128;
    return project([Math.sin(theta) * Math.cos(phi), Math.cos(theta), Math.sin(theta) * Math.sin(phi)]);
  }));
}
for (let j = 0; j < 8; j++) {
  const phi = j * Math.PI / 4;
  grid.push(Array.from({ length: 65 }, (_, i) => {
    const theta = i * Math.PI / 128;
    return project([Math.sin(theta) * Math.cos(phi), Math.cos(theta), Math.sin(theta) * Math.sin(phi)]);
  }));
}
const rim = Array.from({ length: 129 }, (_, i) => project([Math.cos(i * 2 * Math.PI / 128), 0, Math.sin(i * 2 * Math.PI / 128)]));
const path = [project(data.means[0], 1.008)];
for (let i = 1; i < TOTAL; i++) {
  for (let j = 1; j <= 5; j++) path.push(project(slerp(data.means[i - 1], data.means[i], j / 5), 1.008));
}

const frames = Array.from({ length: 100 }, (_, i) => {
  const t = Math.min(1, i / 88);
  const progress = 1 + (TOTAL - 1) * t ** 2;
  const n = Math.floor(progress);
  const fractional = progress - n;
  const current = fractional > 0 ? slerp(data.means[n - 1], data.means[n], fractional) : data.means[n - 1];
  const error = distance(current, CENTER);
  if (!Number.isFinite(error) || error <= 0) throw new Error('Invalid geodesic error.');
  const tailEnd = Math.floor((progress - 1) * 5) + 1;
  return {
    progress, n, error,
    mean: project(current, 1.018),
    sampleCount: Math.min(TOTAL, n + (fractional > 0 ? 1 : 0)),
    activeSample: fractional > 0.01 && n < TOTAL ? project(data.samples[n], 1.012) : null,
    path: path.slice(Math.max(0, tailEnd - 61), tailEnd),
    errorArc: Array.from({ length: 17 }, (_, j) => project(slerp(current, CENTER, j / 16), 1.008)),
    errors: [...data.errors.slice(0, n).map((value, index) => [index + 1, value]), ...(fractional > 0 ? [[progress, error]] : [])],
  };
});

await writeFile(resolve(outputFile), JSON.stringify({
  seed: data.seed, total: TOTAL, radius: RADIUS, stepConstant: A,
  errors: data.errors, grid, rim, truth: project(CENTER, 1.012),
  samples: data.samples.map(point => project(point, 1.006)), frames,
}));
console.log(`Projected ${frames.length} frames using the original simulation and Three.js camera.`);
