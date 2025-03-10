# Object tracking

The tracking step consists in rebuilding object trajectories appearing in a video according to detection results.
It can be achieved in a Single Camera Setup (SCS) or in a Multi Camera Setup (MCS).
The quality of the results highly depends on quality of the input data, i.e.:
* the coverage of the camera(s), to so that every tracked object can be captured at anytime;
* the detector accuracy, so that every tracked object is indeed detected;
* the camera parameters, to get accurate world coordinates
* the video rate, so that the consecutives of each tracked object is close.

## Single Camera Setup
### Preliminaries

The SCS data is typically obtained using `arena-yolo-tracking -i ... -j ...`.
```bash
arena-yolo-tracking -i remap/remap_north_front.mp4 -j json/yolov8/remap_north_front.json --yolo-version 8
```

### Temporal clusteing

The `arena-temporal-clustering` application infers trajectories by matching detections obtained from consecutive frames from a given camera.
The input file is typically obtained using `arena-yolo-tracking -i ... -j ...`.
The trajectories are inferred by assuming that the consecutive positions of a tracked object are close.
The temporal clustering relies on the [Hungarian algorithm](https://en.wikipedia.org/wiki/Hungarian_algorithm) to gather close consecutive detections (and thus, supposed to be related to the same object).
```bash
arena-temporal-clustering -i json/yolov8/remap_north_front.json -o trajectories_remap_north_front.json
```

## Multi-Camera setup
### Preliminaries

The MCS data is typically obtained using `arena-yolo-tracking -i ... -j ...` for each camera.
```bash
for filename_mp4 in $(find remap/points0/ -type f -name "*.mp4")
do
    filename_json="json/$(basename -s .mp4 $filename_mp4).json"
    arena-yolo-tracking -i $filename_mp4 -j json/yolov8/$filename_json --yolo-version 8
done
```

### Spatio-temporal clustering

The `arena-spatio-temporal-clustering` application infers unified trajectories by matching detections obtained from consecutive frames from multiple cameras.
It first runs the spatial clustering, frame-by-frame, to unify the detections provided by all the cameras.
Then, it runs the temporal clustering as if the experiment was running in a single camera setup.
```bash
arena-spatio-temporal-clustering -i json/yolov8/remap_*.json -o trajectories_yolov8.json
```

### Multi-temporal clustering

The `arena-spatio-temporal-clustering` application infers trajectories locally to each camera.
If a tracked object is lost, the impacted camera falls back to the closest detection provided by another camera.
The fallback detection is ignored if it is too far from the last observed detection's position.
```bash
arena-multi-temporal-clustering -i json/yolov8/remap_*.json -o trajectories_yolov8.json
```
