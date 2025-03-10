# Experiments
## Input videos

This section presents two ways to get the videos used by the project.
* Using RAW videos (long path)
* Using remapped videos (fast path)

### RAW videos

We now get and prepare the remapped videos from raw videos retrieved from the cameras.

* Create the `input/`, `output/`, `remap/` directories in the root directory of the project:

```bash
cd ~/arena
mkdir input remap output
```

* Get the input raw videos.
  * If you are on `lambdav2.nbl.nsn-rdnet.net`,
    ```bash
    cd ~/arena
    ln -s /data/arena/input/
    ```

  * Otherwise, [download the input videos](https://nokia.sharepoint.com/sites/NokiaArenaInnovationProject766/_layouts/15/stream.aspx?id=%2Fsites%2FNokiaArenaInnovationProject766%2FShared%20Documents%2FGeneral%2Ftest%20material%2FINTERNAL%20MATERIAL%2Finternally%20shared%20material%2FCONFIDENTIAL%5Ftappara%5Filves%5Fclips%2Fraw%20clips%2FNorth%5FGoal%5FCam%2FQ360%5F20220603%5F212625%5F000075%2EMOV) `Q360_20220603_212625_000075.MOV` in the `~/arena/input/` directory.


* [List the video streams](https://superuser.com/questions/1479702/how-to-list-streams-with-ffmpeg) by using `ffprobe`. It shows that `Q360_20220603_212625_000075.MOV` provides two video streams, namely `0:0` and `0:1`:

```bash
ffprobe -i input/Q360_20220603_212625_000075.MOV
```

* Extract each stream `ffmpeg`. Note that only the front video (`0:0`) is relevant.

```bash
ffmpeg -i input/Q360_20220603_212625_000075.MOV -map 0:0 -c copy input/raw_north_back.mov
ffmpeg -i input/Q360_20220603_212625_000075.MOV -map 0:1 -c copy input/raw_north_front.mov
# ...
```

* Remove the [distorsion](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html) introduced by the camera lense:

```bash
for anchor in "north" "northwest" "northeast" "south" "southwest" "southeast"
do
    arena-remap --input input/raw_$anchor_front.mov --output remap/remap_$anchor_front.mp4
done
```

### Remapped videos

If you are a `lambdav2.nbl.nsn-rdnet.net` user, a larger dataset is stored in `/data/arena`.

To avoid to create redundate data, create the following symbolic links:
```bash
cd ~/arena
ln -s /data/arena/remap/
```

## Pipeline

The shell script below illustrates how to orchestrate some of these binaries in the Arena use case.

```
~/arena/
    remap/point0/remap_southwest.mp4
    remap/point0/remap_northwest.mp4
    remap/point0/remap_south.mp4
    remap/point0/remap_northeast.mp4
    remap/point0/remap_southeast.mp4
    remap/point0/remap_north.mp4
```

Create `~/arena/run.sh`:
```bash
#!/usr/bin/env bash
# This file is part of the hockeytracking project
# https://gitlabe2.ext.net.nokia.com/mandrews/hockeytracking

# Set YOLO_VERSION to 3 (YOLOv3, no segmentation) or 8 (YOLOv8, GPU only)
YOLO_VERSION=3
DETECTOR="yolov${YOLO_VERSION}"

# Range of input frames.
# 0 <= FRAME_START < FRAME_END < 3600
FRAME_START=3000
FRAME_END=3005
# Pass FRAMES="" to process the entire videos
FRAMES="--frame-start $FRAME_START --frame-end $FRAME_END"

# Project folders
ARENA_DIR="${HOME}/arena"
INPUT_VIDEO_DIR="${ARENA_DIR}/remap/point0"
OUTPUT_VIDEO_DIR="${ARENA_DIR}/output/${DETECTOR}"
OUTPUT_JSON_DIR="${ARENA_DIR}/json/${DETECTOR}"

# Bash colors
GREEN="\033[0;32m"
RED="\033[0;31m"
NC="\033[0m"

# Prints and calls an arbitrary bash command
run() {
    cmd=$1
    echo -e "$GREEN$cmd$NC"
    $cmd
}

# Prints an error message
error() {
    msg=$1
    echo -e "$RED$msg$NC" >&2
}

# Single Camera Setup pipeline
pipeline_scs() {
    # Processes each Arena anchor
    for anchor in "north" "northwest" "northeast" "south" "southwest" "southeast"
    do
        # Checks whether the input video is here
        input_video="${INPUT_VIDEO_DIR}/remap_${anchor}.mp4"
        if ! [ -f $input_video ]
        then
            error "$input_video not found"
            continue
        fi

        # Runs the YOLO detection"
        output_video="${OUTPUT_VIDEO_DIR}/detections_${anchor}.mp4"
        detections_json="${OUTPUT_JSON_DIR}/detections_${anchor}.json"
        run "arena-yolo-tracking $FRAMES -i "$input_video" -o $output_video -j $detections_json --show-minimap --yolo-version ${YOLO_VERSION}"

        # Runs the temporal clustering to infer trajectories from a single camera (SCS -- Single Camera Setup)
        trajectories_json="${OUTPUT_JSON_DIR}/trajectories_${anchor}.json"
        animation_html="${OUTPUT_VIDEO_DIR}/trajectories_${anchor}.html"
        run "arena-temporal-clustering $FRAMES -i $detections_json -o $trajectories_json --output-animation $animation_html"
    done
}

# Multi Camera Setup pipeline
# Run pipeline_scs first so that the JSON detections file are created
pipeline_mcs() {
    # Runs the temporal clustering to infer trajectories from multiple camera
    trajectories_json="${OUTPUT_JSON_DIR}/clustered_trajectories.json"
    animation_html="${OUTPUT_VIDEO_DIR}/clustered_trajectories.html"
    run "arena-spatio-temporal-clustering ${FRAMES} -i ${OUTPUT_JSON_DIR}/detections_*.json -o $trajectories_json --output-animation $animation_html"
}

# Runs the Arena pipeline
main() {
    # Creates the output folders
    mkdir -p "$OUTPUT_JSON_DIR" "$OUTPUT_VIDEO_DIR"

    # Calls the pipelines
    pipeline_scs
    pipeline_mcs
}

main
```

Run the script:
```bash
cd ~/arena
chmod a+x run.sh
./run.sh
```
