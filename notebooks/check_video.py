"""Separate encoder smoke check: python3 notebooks/check_video.py."""

from pathlib import Path
from tempfile import TemporaryDirectory

import imageio_ffmpeg

from kaleion import Collection, F, Motion, Workspace
from kaleion.viewers.video import write_mp4


def main():
    arrangement = Collection.sequence(3).arrange(F.s, 0)
    workspace = Workspace({"points": arrangement})
    forward = workspace.set("points", arrangement.place(F.x + 1, 0), motion=Motion.arc())
    backward = workspace.undo()
    frames = [step.frame("points", t) for step in (forward, backward) for t in (0, 0.5, 1)]
    with TemporaryDirectory() as directory:
        path = write_mp4(frames, Path(directory) / "smoke.mp4", size=(480, 320), fps=6)
        count, seconds = imageio_ffmpeg.count_frames_and_secs(str(path))
        assert count == 6 and abs(seconds - 1) < 0.05, (count, seconds)
        reader = imageio_ffmpeg.read_frames(str(path))
        try:
            metadata = next(reader)
            first = next(reader)
            assert tuple(metadata["size"]) == (480, 320), metadata
            assert len(first) == 480 * 320 * 3
        finally:
            reader.close()
        print("Video smoke check passed: six decoded 480×320 H.264 frames, 6 fps, one second.")


if __name__ == "__main__":
    main()
