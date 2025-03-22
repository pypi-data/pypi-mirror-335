# myimagelib release note

## v1.5

- Lose weight project: the current package spreads very broadly. The reuse rates of most functions are quite low. Therefore, I'm planning to remove functions that are not useful any more, and figure out a focus of this package.
  - remove `xcorr_funcs.py` and `fit_circle_utils.py`
  - add frequently used functions to `__init__.py`
- clean up the imports
- add a function `imfindcircles()` based on Atherton 1999

### v1.5.1

- Reorganize the documentation.

### v1.5.2

- Improve `imfindcircles()` with new strong edge criterion and multi-stage detection.

### v1.5.3

- Fix a distance filter bug.

### v1.5.4

- `imfindcircles()` now exclude overlap using `max_radius`

## v1.4

- Implement doctest to test the code automatically.
- Add release note.
- Remove GitHub action that automatically builds docs. Instead build docs manually and upload to the "gh-pages" branch. See code notes for procedures.
- Add `update_mask` to `compact_PIV`.
- Add `to_csv` to `compact_PIV`.
- Handle NaN values in `to8bit`.

## v1.3 

1. Fix the documentation. Due to the folder structure change, autodoc does not work correctly, and all the documentations currently are not working. Fix it in the next release. 

## v1.2 

1. Reorganize the repo as a PyPI package and publish on PyPI.

## v1.1 

1. All the functions and scripts that output PIV data should put PIV in a .mat container, which only save x, y, mask, labels in formation once, and save u, v as 3D arrays. 

2. The operations that based on \*.tif images should be transformed to work on raw images. The affected operations are: 

- PIV
- gen_preview
- remove_background