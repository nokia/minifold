# Preliminaries
## Steps

To track objects of interest appearing in a video, the main steps are:
1. Camera calibration
2. Video preprocessing (based on the camera calibration)
3. Object detection (based on the preprocessed video)
4. Object tracking (based on the detections)

Each of these tasks correspond to one or more `arena-` binaries, depending on the data, the use case, and the adopted approach.

## Command-line arguments

* Each `arena-` binary supports the `--help` option, which displays the list of supported arguments.
* Most of the `arena-`  binaries depend on intrinsic and/or extrinsic camera parameters.  loaded from an input JSON file (`--camera`).
  * In general, these parameters are loaded from an input JSON file (`--camera`). Such a JSON file is generated using `arena-calibrate`.
  * For the Arena use case, if `--camera` is not supplied, camera parameters can be loaded from the `arena` itself. The camera position is inferred from the input video filename. Then, the arena package loads the corresponding camera parameters.

## Video player

When an `arena-` plays a video:
* press _Space_  to pause the video;
* press _Esc_ to quit the video.
