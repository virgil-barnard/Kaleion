"""Portable 1D/2D MP4 rendering of the same snapshots/frames used by Plotly.

This is a separate raster renderer, not a recording of the Plotly UI. 3D camera
interaction belongs to the Plotly adapter; project into 2D explicitly for video.
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont
import imageio_ffmpeg

from ._display import BACKGROUND, FOREGROUND, GRID, bounds, series


def write_mp4(samples, path, *, labels=None, title="Kaleion · motion", fps=24,
              size=(960, 640), connect=False):
    """Write H.264 MP4 at fixed bounds and equal spatial scale; return its Path.

    Render every supplied sample once. Repeat samples explicitly for pauses or
    slower exact-case playback. The encoder comes from imageio-ffmpeg's wheel
    on supported platforms, or IMAGEIO_FFMPEG_EXE can name a local executable.
    """
    if not np.isfinite(fps) or fps <= 0:
        raise ValueError("fps must be positive")
    if len(size) != 2 or any(isinstance(n, bool) or not isinstance(n, int) or n < 240 or n % 2 for n in size):
        raise ValueError("Video width and height must be even integers of at least 240")
    data, labels = series(samples, labels)
    if data[0].positions.shape[1] != 2:
        raise ValueError("MP4 supports 1D/2D; explicitly project 3D arrangements before capture")
    path = Path(path)
    if path.suffix.lower() != ".mp4":
        raise ValueError("Use an .mp4 output path")
    extent = bounds(data)
    width, height = size
    scale = min((width - 90) / (extent[0][1] - extent[0][0]),
                (height - 180) / (extent[1][1] - extent[1][0]))
    center = np.array([(a + b) / 2 for a, b in extent])
    font = ImageFont.load_default(size=17)
    small = ImageFont.load_default(size=13)
    heading = ImageFont.load_default(size=23)
    background = np.array(ImageColor.getrgb(BACKGROUND))

    def raster(sample, caption):
        canvas = Image.new("RGB", size, BACKGROUND)
        draw = ImageDraw.Draw(canvas)
        draw.text((35, 24), title, font=heading, fill=FOREGROUND)
        draw.text((35, 59), caption, font=font, fill=FOREGROUND)
        footer = "Presentation frames · exact integer labels · amber = incidence · purple = changing"
        if sample.status != "ready":
            footer = sample.status
        draw.text((35, height - 30), footer, font=small, fill=FOREGROUND)
        points = (sample.positions - center) * [scale, -scale] + [width / 2, (height + 50) / 2]
        if connect and len(points) > 1:
            draw.line([tuple(p) for p in points], fill=GRID, width=2)
        for (x, y), label, color, alpha in zip(points, sample.labels, sample.colors, sample.opacity):
            if alpha <= 0:
                continue
            rgb = np.array(ImageColor.getrgb(color))
            fill = tuple(np.rint(alpha * rgb + (1 - alpha) * background).astype(int))
            text = tuple(np.rint(alpha * np.array(ImageColor.getrgb(FOREGROUND))
                                 + (1 - alpha) * background).astype(int))
            draw.ellipse((x - 15, y - 15, x + 15, y + 15), fill=fill)
            if len(label) <= 12:
                draw.text((x, y - 1), label, font=small, fill=text, anchor="mm",
                          stroke_width=1, stroke_fill=BACKGROUND)
        return canvas.tobytes()

    path.parent.mkdir(parents=True, exist_ok=True)
    # Replace the destination only after encoding succeeds; no partial old export.
    with NamedTemporaryFile(suffix=".mp4", dir=path.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        writer = imageio_ffmpeg.write_frames(
            str(temporary_path), size, fps=fps, codec="libx264", pix_fmt_out="yuv420p",
            macro_block_size=2, ffmpeg_log_level="error", output_params=["-movflags", "+faststart"],
        )
        try:
            writer.send(None)
            for sample, label in zip(data, labels):
                writer.send(raster(sample, label))
        finally:
            writer.close()
        # The wrapper may close without raising on some encoder failures.
        count, _ = imageio_ffmpeg.count_frames_and_secs(str(temporary_path))
        if count != len(data):
            raise RuntimeError(f"Video encoded {count} of {len(data)} frames")
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)
    return path
