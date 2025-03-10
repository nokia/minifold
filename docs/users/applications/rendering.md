# Video rendering

## Digital twin

The `arena-digital-twin` takes advantage of the results of a detector (e.g., `arena-yolo-tracking`) and allows to display
an arbitrary frame, using an arbitrary scene and an arbitrary camera pose.

```bash 
arena-digital-twin -i remap/point0/remap_north_front.mp4 --scene arena --json-scs json/yolov8/remap_north.json --frame-index 3316
```
