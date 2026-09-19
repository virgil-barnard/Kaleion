# Lesson previews

These PNGs are exported from Plotly figures in the executed notebooks with their default parameters. No mathematical construction is duplicated in the gallery exporter. It selects an existing figure and, where specified, an existing recorded frame; then it shortens the title, hides playback controls, adjusts the framing, and sizes the image to 960 × 600. Lesson 02's notation panel is omitted at thumbnail size; its full argument remains in the notebook. The Young diagram's camera faces the halfway plane so its cells remain distinguishable.

| Image | Notebook | Selected view |
| --- | --- | --- |
| `01-spiral.png` | [01 · Discovery workbench](../../../notebooks/01_discovery_workbench.ipynb) | Exact spiral case `n = 4`, frame `3` |
| `02-floor-sums.png` | [02 · Floor sums](../../../notebooks/02_floor_sum_proof.ipynb) | Both incidences, coprime case `(11, 7)` |
| `03-three-incidences.png` | [03 · Three incidences](../../../notebooks/03_three_incidence_box.ipynb) | All three solids, `(11, 7, 5)` |
| `04-measured-motion.png` | [04 · Measured motion](../../../notebooks/04_measured_motion.ipynb) | After adding `h_X` and `h_Y`, frame `25` |
| `05-finite-radon.png` | [05 · Finite Radon](../../../notebooks/05_finite_radon.ipynb) | Modular line `y − 2x ≡ 1 (mod 5)`, frame `2:1` |
| `06-young-layers.png` | [06 · Young layers](../../../notebooks/06_young_layers.ipynb) | Halfway through the recorded 3D turn, frame `10` |
| `07-additive-structure.png` | [07 · Additive structure](../../../notebooks/07_additive_structure.ipynb) | Completed stacking by measured rank, frame `41` |
| `08-ehrhart-counts.png` | [08 · Ehrhart counts](../../../notebooks/08_ehrhart_counts.ipynb) | Exact dilation `n = 6`, frame `6` |
| `09-norm-fibers.png` | [09 · Norm fibers](../../../notebooks/09_norm_fibers.ipynb) | Six measured norm fibers in 3D, `p = 7` |
| `10-hermitian-partitions.png` | [10 · Hermitian partitions](../../../notebooks/10_hermitian_partitions.ipynb) | Seven groups of four, frame `49`; fitted axes with independent screen scales |

## Regenerate

First execute all ten notebooks with default parameters, following the [notebook instructions](../../../notebooks/README.md#execute-without-the-ui). Their populated copies belong in `build/notebooks/*.executed.ipynb`; the source notebooks remain cleared.

From the repository root, with the notebook environment activated:

```sh
python3 notebooks/export_gallery.py
```

Open the resulting `build/readme-gallery/*.html` files in a browser. Each plot's **Download plot as png** camera button exports the correct filename and dimensions. Replace the corresponding PNG here. The HTML files share an adjacent `plotly.min.js` and work offline when kept together. This path uses only the existing notebook dependencies.

For optional batch PNG export, install Kaleido in the development environment and supply a compatible Chrome/Chromium installation, as described by [Plotly](https://plotly.com/python/static-image-export/):

```sh
python3 -m pip install kaleido
python3 notebooks/export_gallery.py --png-dir docs/images/lessons
```

Chrome can be installed separately, or with `plotly_get_chrome`. Kaleido and Chrome are needed only for this optional export command; they are not Kaleion runtime or notebook dependencies. The checked-in images were exported with Plotly.js in Chromium using the same figure data and dimensions.

Review image contents, captions, and sizes before committing. If default lesson parameters or motion sampling change, update the explicit selections in [export_gallery.py](../../../notebooks/export_gallery.py) and this table together. Keep generated HTML, executed notebooks, and videos under `build/`; only the small curated previews belong here.

GitHub supports [static images](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files#rendering-and-diffing-images), but its notebook preview [does not run JavaScript plots](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files#working-with-jupyter-notebook-files-on-github). The README links each image to its source lesson. Interactive views are available by running the notebook or opening its generated standalone HTML.
