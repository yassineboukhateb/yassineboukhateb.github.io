# Barycenter Illustration Export

The projector uses the original animation's `math.mjs` and vendored Three.js camera. The renderer draws the projected geometry and convergence curve directly at 1800 x 722 pixels; it does not enlarge an existing image.

```sh
node _tools/barycenter/project.mjs /path/to/barycenter-animation /tmp/barycenter-hd.json
python _tools/barycenter/render.py /tmp/barycenter-hd.json /tmp/barycenter-preview --preview
python _tools/barycenter/render.py /tmp/barycenter-hd.json assets/illustrations/barycenter
```

Rendering requires Matplotlib, NumPy, and Pillow with animated WebP support. The primary WebP export is lossless and checked against a rendered frame. A palette-based GIF is retained as a compatibility fallback, with a lossless PNG poster for reduced-motion preferences. The dashed curve is a rate reference, not a pathwise bound.
