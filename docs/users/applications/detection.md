# Object detection and segmentation


The detection step consists in finding objects of interest in an input frame/video.
In general, the detection is characterized by a bounding rectangular box.

Some detectors, like YOLOv8, can furthermore segment the detection (_i.e._, find the mask of pixels corresponding to each object of interest).
Such masks are exported using polylines to get smaller and more comprehensive JSON output files.

## Foreground extraction

The `arena-foreground` application updates frame-by-frame a [background model](https://learnopencv.com/simple-background-estimation-in-videos-using-opencv-c-python/).
Then, for each frame, it compares the background model and the current frame by applying a [background subtraction](https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html) to deduce players' contours.

```bash
arena-foreground -i remap/remap_north_front.mp4 -o output/foreground_north_front.mp4
```

## YOLO

The `arena-yolo-tracking` application detects humans using YOLO (You Only Look Once) appearing in an output video (`-i`).
The detections are showed in the played video, which may be saved to an output file (`-o`)

Currently, only [YOLOv3](https://pjreddie.com/darknet/yolo/) and [YOLOv8](https://docs.ultralytics.com/) are supported (`--yolo-version`). By default, YOLOv3 is used.
* You must choose YOLOv3 if the running machine has no GPU, as YOLOv8 requires a GPU.
* Both YOLOv3 and YOLOv8 output detection boxes.
* If you need detection masks (segmentation), use YOLOv8.

Once the video is processed, the results can be dumped to an output file (`-j`).


* YOLOv3:

```bash
arena-yolo-tracking -i remap/remap_north_front.mp4 -o output/yolov3_north_front.mp4
arena-yolo-tracking -i remap/remap_north_front.mp4 -o output/yolov3_north_front.mp4 --yolo-version 3 -j json/yolov3/remap_north_front.json
```

* YOLOv8: ensure your machine has a GPU

```bash
arena-yolo-tracking -i remap/remap_north_front.mp4 -o output/yolov8_north_front.mp4 --yolo-version 8 -j json/yolov8/remap_north_front.json
```

Many other options are available, see `arena-yolo-tracking --help` for further details.

## HOG

The `arena-hog-tracking` application detects humans using [HOG (Histogram of Oriented Gradients)
and NMS (Non-Max Suppression)](https://pyimagesearch.com/2015/11/09/pedestrian-detection-opencv/).

```bash
arena-hog-tracking -i remap/remap_north_front.mp4 -o output/hog_north_front.mp4
```

## MOG

The `arena-mog-tracking` application detects humans using [MOG (Mixture Of Gaussians)](https://www.geeksforgeeks.org/python-opencv-background-subtraction/).

```bash
arena-mog-tracking -i remap/remap_north_front.mp4 -o output/mog_north_front.mp4
```
