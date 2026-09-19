# Notebook viewer validation

Checked with Python 3.12.14, NumPy 2.3.5, Plotly 6.9.0, JupyterLab 4.6.3,
IPython 9.17.1, Pillow 12.3.0, and imageio-ffmpeg 0.6.0.

- Editable installation with `.[notebooks]` succeeded. A fresh core import does not load Plotly.
- `python3 -m unittest discover -s tests -v`: 38 tests passed, including eight presentation tests for exact labels, incidence states, zero-opacity creation, reversed labels, fixed motion bounds, empty/3D views, and failed evaluation visibility.
- `python3 examples/discovery.py --out build/example-output`: reference results unchanged.
- `python3 notebooks/check_video.py`: six H.264 frames decoded at 480×320, 6 fps.
- Wheel build succeeded; notebook source validates as nbformat 4 and has cleared outputs.
- All 15 notebook code cells ran sequentially in a fresh IPython process. The default examples produced counts `[0, 1, 3, 4, 6, 7, 9]`, first column `[0, 11, 22, 33, 44, 55, 66]`, and 24 retained structural hits through 36. Save/reopen and forward/undo assertions passed.
- The generated notebook converted to HTML with 15 interactive figures and two embedded videos. Browser inspection covered the full document and all three standalone exports, with HTTP(S) requests blocked to check local figure operation. The 3D camera was changed and remained in place after advancing animation frames.
- Both MP4 exports decoded at 960×640 and 24 fps: roll/undo has 98 frames (about 4.08 seconds), and the spiral has 204 frames (8.5 seconds). Representative video frames and Plotly screenshots were visually inspected.

## Limits of this check

This execution host prohibits local socket binding, so a normal `nbconvert --execute`
kernel could not start over either TCP or IPC. Cell execution was verified using
IPython's in-process shell and captured rich outputs, not a live JupyterLab kernel
session. The README retains the standard local Jupyter/nbconvert commands.

With Plotly 6.9.0, pressing Pause during active playback emitted an undefined rejected
animation promise in the headless browser console. Pause stopped playback and Restart
returned to the first frame. These cancellation events were recorded rather than
silenced; loading and inspecting the figures succeeded. The initial viewer does not
guarantee a particular 3D playback frame rate or export 3D MP4 video.

These are finite executable examples and rendering checks, not proofs of the
mathematical patterns they display.
