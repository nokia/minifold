# Camera calibration
## Overview

The `arena-calibrator` application loads an image or the first frame (`-i`) to calibrate a camera and save the *camera parameters* into an output JSON file (`-j`).

The camera parameters are required for any tool mapping a pixel with a 3D point.
They are split into two categories:
* the *intrinsic parameters* characterize the lens of the camera;
* the *extrinsic parameters* characterize the support of the camera.
If you are not familiar with these notions, see [these slides](https://www.cse.psu.edu/~rtc12/CSE486/lecture13_6pp.pdf).

In practice, the end-user:
1. searches the intrinsic parameters to undistort the frame; 
2. searches the extrinsic parameters using a 3D model, called __scene__ (`--scene`)
These two steps are done by adjusting the sliders of the `arena-calibrator` GUI. Once the 3D model matches the input frame, the camera parameters are found and can be saved to an output JSON file.

## Scenes

Currently, the `arena` package supports the following the `arena` and `maze` scenes.
The `arena` scene models an [IIHF hockey playground](https://stats.iihf.com/hockey/rules/img/sec1.pdf).
The `maze` scene models the UNIX maze facility, located at Murray Hill.

One may implement additional scenes (see the `arena.scenes` module).

## Notations 

The documentation uses the following notations:
* __World frame:__
  * `X` points to the East;
  * `Y` points to the North;
  * `Z` points to the sky.
* __Camera frame:__
  * `x` points to the right of the camera;
  * `y` to the sky;
  * `z` to the horizon.

Using these notations:
* the __extrinsic parameters__ translate `(X, Y, Z)` world coordinates to `(x, y, z)` camera coordinates (and conversely);
* the __intrinsic parameters__ translate `(u, v)` pixels coordinates to `(x, y, z)` camera coordinates (and conversely), under additional assumptions (e.g., every pixel are at Y=0).

## GUI
### Extrinsic parameters

Extrinsic parameters allow to move from the world frame to the camera frame (and conversely). They can be interpreted according to the _camera frame_.
* __Rotation:__ (see [Tait–Bryan angles](https://en.wikipedia.org/wiki/Euler_angles#Chained_rotations_equivalence)). They model three consecutive rotations, and are thus quite intuitive to tune. The Tait–Bryan angles can be converted afterwards to a rotation vector (in radians), that model a single rotation around an arbitrary vector defined in the Camera frame. Note that OpenCV functions generally rely on rotation vectors.
  * `pitch`: rotation around the `y`-axis (in °);
  * `yaw`: rotation around the `z`-axis (in °);
  * `roll`: rotation around the `x`-axis (in °).
* __Translation vector:__ transform the Camera origin to the World origin in the Camera frame.
  * `tx`: translation vector, `x`-axis (in dm) -- horizontal shift;
  * `ty`: translation vector, `y`-axis (in dm) -- vertical shift;
  * `tz`: translation vector, `z`-axis (in dm) -- zoom in/out.

### Intrinsic parameters

Intrinsic parameters allow to translate pixels to coordinates in the camera frame (and conversely) under additional assumptions (e.g., every pixel lie on a flat ground).
* __Focal length:__
  * `fx`: focal length, `x`-axis (in dm);
  * `fy`: focal length, `y`-axis (in dm);
* __Principal point:__
  * `cx`: principal point, `x`-axis (in dm);
  * `cy`: principal point, `y`-axis (in dm);

## Usage

The sliders of the GUI tune the camera parameters. The frame and the eventual scene are rendered consequently. To quit:
* Press `Esc` to save the results to the eventual output JSON file (`-j`);
* Press `Ctrl-C` to quit without saving the results to the eventual output JSON file (`-j`).

### Distorted frame

_Step 1:_ At this step, loading a scene (`--scene`) is not required.
Note that without the `--scene` argument, the sliders related to the extrinsic parameters are irrelevant and thus not displayed.
```bash
arena-calibrator -i input/raw_north_front.mov \
    -j ~/.arena/camera/arena/raw_north_front.json
    --rotation 270 --direction vertical
```

_Step 2:_ Calibrate the intrinsic parameters:

  1. Place the cyan disc so that it roughly matches the principal point by modifying `cx` and `cy`.
  2. Undistort as much as possible the input frame by altering `fx`, `fy` and `dist`.
  3. Repeat the procedure until getting an undistorted frame. Then, press `Esc` to save and quit.

_Step 3:_ If you plan to process distorted frames to a tool, re-run the calibrator by charging the adequate scene (otherwise, skip this step):
```bash
arena-calibrator -i input/raw_north_front.mov \
    -j ~/.arena/camera/arena/raw_north_front.json \
    --rotation 270 --direction vertical \
    --scene ScenePlaygroundIihf
```
Note that in the previous command, we passed option related to camera preprocessing (to flip and rotate the input frame) which corresponds to the `rot` and `flip` sliders.
To do so, follow the steps listed in the [Extrinsinc parameters calibration](./calibration.html#id4) section.

_Step 4:_ [Undistort](https://en.wikipedia.org/wiki/Distortion_%28optics%29) the video using `arena-remap`:
```bash
arena-remap -i input/raw_north_front.mov \
    --camera ~/.arena/camera/arena/raw_north_front.json \
    -j ~/.arena/camera/arena/remap_north_front.json \
    -o remap/remap_north_front.mp4
```
Follow the steps listed in the *Extrinsinc parameters calibration* section.

Then, follow the steps listed in the [Extrinsinc parameters calibration](./calibration.html#id4) section.

### Undistorted frame, first calibration

The following example shows how to run the calibration using the first frame of the input video, using default Arena North camera parameters.
```bash
arena-calibrator -i remap/remap_north_front.mp4 \
    --scene ScenePlaygroundIihf \
    -j ~/.arena/camera/arena/remap_north_front.json
```
Then, follow the steps listed in the [Extrinsinc parameters calibration](./calibration.html#id4) section.

### Recalibration
#### From a `.json` file

Assume we want to recalibrate the camera parameters defined in `~/.arena/camera/arena/remap_north_front.json` and related to the `remap/remap_north_front.mp4` video.
```bash
arena-calibrator -i remap/remap_north_front.mp4 \
    --scene ScenePlaygroundIihf \
    --camera ~/.arena/camera/arena/remap_north_front.json \
    -j ~/.arena/camera/arena/remap_north_front.json
```
Then, follow the steps listed in the [Extrinsinc parameters calibration](./calibration.html#id4) section.

#### From a `Camera` instance provided by the package

If the `Camera` provided by the `arena` package are inaccurate, use the script below to dump each of them into a dedicated JSON file.

```python
import json
from pathlib import Path
from arena import get_camera_anchor_from_filename, get_camera_from_anchor

CONF_DIR = Path.home() / ".arena" / "camera" / "arena"
for filename_jpg in list(ARENA_DIR.glob("*.jpg")):
    anchor = get_camera_anchor_from_filename(filename_jpg)
    camera = get_camera_from_anchor(anchor)
    filename_json = CONF_DIR / (filename_jpg.with_suffix("").name + "_front.json")
    if filename_json.exists():
        print(f"{filename_json} already exists")
    else:
        with open(filename_json, "w") as f:
            print(f"Writting {filename_json}")
            print(json.dumps(camera.to_dict(), indent=4), file=f)
```
Then, recalibrate each output file as explained in the previous section.
See the last section to see possible recalibrations.

### Extrinsinc parameters calibration

Try to not modify `cx`, `fx`, `fy` and `dist` (intrinsic parameters).
As `cy` is harder to calibrate, you might need to adjust it.

1. Calibrate roughly `tx`, `ty`, `tz` to see the scene.
2. Calibrate `roll` so that the playground lines are coplanar with the playground.
3. Calibrate `yaw` and `pitch` so that the playground lines going to the principal point are correctly oriented.
4. Adjust `tx`, `ty`, `tz`, `cy` to make the scene lines match the frame. Then, press `Esc` to save and quit.

## Examples

This section lists JSON files obtained for various input frames/videos.
You may reload them using the `--camera` options for most of the `arena-...` commands and try to improve them using `arena-calibrator`.

### Arena (`raw_north_camera`)
#### `~/.arena/camera/arena/raw_north.json`

```json
{
    "kmat": [
        [
            1598.2,
            0.0,
            1919.5000000000002
        ],
        [
            0.0,
            1750.2,
            1900.1
        ],
        [
            0.0,
            0.0,
            1.0
        ]
    ],
    "rvec": [
        0.06258620942301661,
        2.1824703055199257,
        -2.1988806528657916
    ],
    "tvec": [
        [
            -1.1
        ],
        [
            2.3
        ],
        [
            32.9
        ]
    ],
    "dist": -0.214,
    "anchor": "N",
    "color": "#008b8b"
}
```

#### `~/.arena/camera/arena/remap_north_front.json`

```json
{
    "kmat": [
        [
            970.7,
            0.0,
            2001.4
        ],
        [
            0.0,
            1125.0,
            1822.4
        ],
        [
            0.0,
            0.0,
            1.0
        ]
    ],
    "rvec": [
        [
            -0.2346
        ],
        [
            2.1967
        ],
        [
            -2.1795
        ]
    ],
    "tvec": [
        [
            -1.728
        ],
        [
            2.0408
        ],
        [
            29.7122
        ]
    ],
    "anchor": "N",
    "color": "#008b8b"
}
```

#### `~/.arena/camera/arena/remap_south_front.json`

```json
{
    "kmat": [
        [
            1194.9,
            0.0,
            1949.0
        ],
        [
            0.0,
            1156.8,
            1886.0
        ],
        [
            0.0,
            0.0,
            1.0
        ]
    ],
    "rvec": [
        1.5410945803248157,
        -0.05767313761383726,
        0.038566353836660655
    ],
    "tvec": [
        [
            -2.6
        ],
        [
            3.3
        ],
        [
            30.5
        ]
    ],
    "dist": 0.0,
    "anchor": "S",
    "color": "#ffa500"
}
```

### UNIX maze

To calibrate using the UNIX maze scene, use ``--scene SceneUnixMaze``.

#### `~/.arena/camera/unix_maze/area1.json`

```json
{
    "kmat": [
        [
            1055.5,
            0.0,
            499.0
        ],
        [
            0.0,
            1025.0,
            166.5
        ],
        [
            0.0,
            0.0,
            1.0
        ]
    ],
    "rvec": [
        2.1418957835845127,
        2.174642040065358,
        -0.2067511643156553
    ],
    "tvec": [
        [
            -10.9
        ],
        [
            -6.3
        ],
        [
            11.5
        ]
    ],
    "dist": 0.0,
    "anchor": "?",
    "color": "#00ff00"
}
```

#### `cam15_00000_crop2.json`

```json
{
    "kmat": [
        [
            937.2,
            0.0,
            452.1
        ],
        [
            0.0,
            966.7,
            401.8
        ],
        [
            0.0,
            0.0,
            1.0
        ]
    ],
    "rvec": [
        -0.027816307417616027,
        -2.656164596506513,
        1.6565345976806778
    ],
    "tvec": [
        [
            4.7
        ],
        [
            -6.3
        ],
        [
            20.9
        ]
    ],
    "dist": 0.0,
    "anchor": "?",
    "color": "#00ff00"
}
```

### Warehouse
#### `~/.arena/camera/unix_maze/warehouse.json`

```json
{
    "kmat": [
        [
            132.7,
            0.0,
            608.0
        ],
        [
            0.0,
            119.9,
            304.0
        ],
        [
            0.0,
            0.0,
            1.0
        ]
    ],
    "rvec": [
        -3.555863523521538e-16,
        -2.2156181428006536,
        2.227249569846617
    ],
    "tvec": [
        [
            5.9
        ],
        [
            1.6
        ],
        [
            15.7
        ]
    ],
    "dist": 0.0,
    "anchor": "?",
    "color": "#00ff00"
}
```
