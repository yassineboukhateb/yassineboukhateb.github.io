"""Render projected scientific geometry directly at high resolution.

Usage: python render.py INPUT_JSON OUTPUT_DIRECTORY [--preview]
Requires Matplotlib, NumPy, and Pillow with animated WebP support.
"""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter
import numpy as np
from PIL import Image


WIDTH, HEIGHT = 1800, 722
LOGICAL_WIDTH, LOGICAL_HEIGHT = 480, 480 * HEIGHT / WIDTH
INK, MUTED, TEAL, ROSE, GRID = "#23332f", "#60736b", "#198a7b", "#ce5876", "#e4eae6"


def render(data):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "text.antialiased": True})
    fig = plt.figure(figsize=(WIDTH / 270, HEIGHT / 270), dpi=270, facecolor="white")

    def axes(left, bottom, width, height):
        return fig.add_axes([left / LOGICAL_WIDTH, bottom / LOGICAL_HEIGHT, width / LOGICAL_WIDTH, height / LOGICAL_HEIGHT])

    def text(x, y, value, **kwargs):
        kwargs.setdefault("color", INK)
        return fig.text(x / LOGICAL_WIDTH, 1 - y / LOGICAL_HEIGHT, value, va="center", **kwargs)

    geometry = axes(6, LOGICAL_HEIGHT - 156, 228, 148)
    geometry.set(xlim=(-1, 1), ylim=(-1, 1))
    geometry.set_axis_off()
    for points in data["grid"]:
        geometry.plot(*np.asarray(points).T, color="#a1b7aa", alpha=0.38, linewidth=0.55, zorder=1)
    geometry.plot(*np.asarray(data["rim"]).T, color="#799989", alpha=0.75, linewidth=0.65, zorder=1)
    samples = geometry.scatter([], [], s=1.8**2, color=TEAL, alpha=0.58, linewidths=0, zorder=2)
    tail, = geometry.plot([], [], color=ROSE, alpha=0.45, linewidth=0.75, zorder=3)
    error_arc, = geometry.plot([], [], color=ROSE, alpha=0.75, linewidth=0.85, zorder=4)
    active_sample, = geometry.plot([], [], marker="o", color=TEAL, markersize=2.6, linestyle="", zorder=5)
    mean_ring, = geometry.plot([], [], marker="o", markersize=6.2, markerfacecolor="none", markeredgecolor=ROSE, markeredgewidth=0.65, linestyle="", alpha=0.7, zorder=6)
    mean, = geometry.plot([], [], marker="o", markersize=4, color=ROSE, linestyle="", zorder=7)
    truth = data["truth"]
    geometry.plot([truth[0]], [truth[1]], marker="+", markersize=5.2, markeredgewidth=0.85, color=INK, linestyle="", zorder=8)
    geometry.annotate("b", truth, xytext=(4, -2), textcoords="offset points", fontsize=10.5, fontstyle="italic", fontfamily="DejaVu Serif", zorder=9)

    convergence = axes(284, 55, 180, 116)
    convergence.set(xscale="log", yscale="log", xlim=(1, data["total"]))
    values = [*data["errors"], *(1 / np.sqrt(np.arange(1, data["total"] + 1)))]
    convergence.set_ylim(max(1e-6, min(values) * 0.60), max(values) * 1.18)
    convergence.xaxis.set_major_locator(FixedLocator([1, 4, 16, 64, 256]))
    convergence.xaxis.set_major_formatter(FuncFormatter(lambda value, _: str(int(value))))
    convergence.yaxis.set_major_locator(FixedLocator([value for value in [0.001, 0.01, 0.1, 1] if convergence.get_ylim()[0] <= value <= convergence.get_ylim()[1]]))
    convergence.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.2g}"))
    convergence.minorticks_off()
    convergence.tick_params(axis="both", labelsize=7.4, length=0, pad=4, colors=MUTED)
    convergence.grid(axis="y", color=GRID, linewidth=0.5)
    convergence.set_axisbelow(True)
    for name, spine in convergence.spines.items():
        spine.set_visible(name == "bottom")
        spine.set_color(GRID)
        spine.set_linewidth(0.6)
    reference_n = np.arange(1, data["total"] + 1)
    convergence.plot(reference_n, 1 / np.sqrt(reference_n), color="#84958c", linewidth=0.7, dashes=(3, 4), zorder=2)
    error_path, = convergence.plot([], [], color=ROSE, linewidth=1, solid_joinstyle="round", zorder=3)
    endpoint, = convergence.plot([], [], marker="o", markersize=3, markerfacecolor=ROSE, markeredgecolor="white", markeredgewidth=0.5, linestyle="", zorder=4)

    text(284, 9, "Convergence", fontsize=9, fontweight="medium")
    live_error = text(451, 9, "", fontsize=8.5, ha="right", fontvariant="normal")
    live_error.set_color(ROSE)
    text(470, 9, "rad", fontsize=7.5, color=MUTED, ha="right")
    text(374, 165, "Sample size n", fontsize=7.6, color=MUTED, ha="center")
    text(250, 79, "Distance (rad)", fontsize=7.6, color=MUTED, ha="center", rotation=90)
    counter = text(120, 185, "", fontsize=8.5, ha="center")

    geometry_handles = [
        Line2D([], [], marker="o", color=TEAL, markersize=2.7, linestyle=""),
        Line2D([], [], marker="o", color=ROSE, markersize=3, linestyle=""),
        Line2D([], [], marker="+", color=INK, markersize=4.5, linestyle=""),
    ]
    fig.legend(geometry_handles, ["Samples", "Iterated mean", "True mean"], loc="center", bbox_to_anchor=(0.25, 1 - 166 / LOGICAL_HEIGHT), ncol=3, frameon=False, fontsize=7.2, handletextpad=0.3, handlelength=0.8, columnspacing=0.75, labelcolor=INK)
    fig.legend([
        Line2D([], [], color=ROSE, linewidth=1),
        Line2D([], [], color="#84958c", linewidth=0.7, dashes=(3, 4)),
    ], ["Error", r"$1/\sqrt{n}$ reference"], loc="center", bbox_to_anchor=(374 / LOGICAL_WIDTH, 1 - 185 / LOGICAL_HEIGHT), ncol=2, frameon=False, fontsize=7.2, handletextpad=0.4, handlelength=1.3, columnspacing=0.9, labelcolor=INK)

    projected_samples = np.asarray(data["samples"])
    for frame in data["frames"]:
        samples.set_offsets(projected_samples[:frame["sampleCount"]])
        tail.set_data(*np.asarray(frame["path"]).T)
        error_arc.set_data(*np.asarray(frame["errorArc"]).T)
        for marker in [mean_ring, mean]:
            marker.set_data([frame["mean"][0]], [frame["mean"][1]])
        active_sample.set_data(*([[frame["activeSample"][0]], [frame["activeSample"][1]]] if frame["activeSample"] else [[], []]))
        error_path.set_data(*np.asarray(frame["errors"]).T)
        endpoint.set_data([frame["progress"]], [frame["error"]])
        live_error.set_text(f"{frame['error']:.3f}")
        counter.set_text(f"n = {frame['n']}")
        fig.canvas.draw()
        pixels = np.asarray(fig.canvas.buffer_rgba())
        assert pixels.shape[:2] == (HEIGHT, WIDTH)
        yield Image.fromarray(pixels).convert("RGB")
    plt.close(fig)


def export(data, destination, preview=False):
    destination.mkdir(parents=True, exist_ok=True)
    if preview:
        data = {**data, "frames": [data["frames"][60]]}
        image = next(render(data))
        image.save(destination / "preview-hd.png")
        print(f"Preview: {destination / 'preview-hd.png'}", flush=True)
        return

    frames = list(render(data))
    poster = destination / "barycenter-hd-poster.png"
    frames[60].save(poster, optimize=True)
    output = destination / "barycenter-hd.webp"
    frames[0].save(output, format="WEBP", save_all=True, append_images=frames[1:], duration=150, loop=0, lossless=True, quality=100, method=4)
    with Image.open(output) as image:
        elapsed = 0
        for i in range(image.n_frames):
            image.seek(i)
            decoded = image.convert("RGB")
            if elapsed <= 9000 < elapsed + image.info["duration"]:
                assert hashlib.sha256(decoded.tobytes()).digest() == hashlib.sha256(frames[60].tobytes()).digest(), "WebP export is not pixel-exact"
                break
            elapsed += image.info["duration"]
        else:
            raise AssertionError("Missing poster timestamp in animation")
        print(f"WebP: {image.size}, {image.n_frames} frames, lossless round trip verified, {output.stat().st_size:,} bytes", flush=True)

    palette_source = Image.new("RGB", (WIDTH, HEIGHT * 3), "white")
    for i, index in enumerate([0, 45, 88]):
        palette_source.paste(frames[index], (0, i * HEIGHT))
    palette = palette_source.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    indexed = [image.quantize(palette=palette, dither=Image.Dither.NONE) for image in frames]
    gif = destination / "barycenter-hd.gif"
    indexed[0].save(gif, save_all=True, append_images=indexed[1:], duration=150, loop=0, disposal=2, optimize=True)
    print(f"GIF fallback: {gif.stat().st_size:,} bytes", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    export(json.loads(args.input.read_text()), args.output, args.preview)
