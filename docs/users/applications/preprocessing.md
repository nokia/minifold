# Video preprocessing

The raw videos captured by a camera are in general distorted, rotated, flipped, etc.
Preprocessing is hence often needed to make them human readable.

## Remap raw videos

The `arena-remap` application remaps an input raw video (`-i`) typically obtained from a camera.
`arena-remap` can rotate and/or flip and/or undistort an input video.
The resulting video is displayed and/or saved to an output file (`-o`).

To undistort the video, `arena-remap` requires camera intrinsic (lens) parameters.

__Example:__ Remaps a video in live using the camera parameters related to the North camera (defined in the `arena` package):
```bash
arena-remap -i input/raw_north_front.mov
```

__Example:__ Advanced example:

_Step 1:_ Calibrate the intrinsic parameters:
```bash
arena-calibrator -i input/raw_north_front.mov \
    -r 90 -d horizontal \
	-j ~/.arena/camera/arena/remap_north_front.json
```
Here, `arena-calibrator` applies:
* a clockwise rotation of `90°` (`-r`);
* an horizontal flip (`-d`).

_Step 2:_ Remap the video:
```bash
arena-remap -i input/raw_north_front.mov \
    -r 90 -d horizontal \
    --camera ~/.arena/camera/arena/raw_north_front.json \
    -j ~/.arena/camera/arena/remap_north_front.json \
    -o remap/remap_north_front.mp4
```
Here, `arena-remap` applies:
* a clockwise rotation of `90°` (`-r`);
* an horizontal flip (`-d`);
* a distortion based on the intrinsic parameters (`--camera`) obtained at step 1 (note that the extrinsic parameters are ignored).

Finally, `arena-remap` saves the remapped video (`-o`) as well as the corresponding camera parameters (`-j`).

_Step 3_ Calibrate extrinsic parameters using `arena-calibrator`:
```bash
arena-calibrator -i remap/remap_north_front.mp4 \
	--camera ~/.arena/camera/arena/remap_north_front.json \
    -j ~/.arena/camera/arena/remap_north_front.json \
	--scene arena
```

## Flattening a 360° video

The `arena-nfov` application flattens 360° videos as those involved in the U23 project.
```bash
arena-nfov -i U23/360-stadium-3_2023-06-11_out_20230611_142510.mp4
```
