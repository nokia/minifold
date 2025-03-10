# Video recording

``arena-record`` save an input stream (e.g., a RSTP stream) to a MP4 file.
As a stream is of arbitrary length, you can fetch a specific number of frames using the `--frame-end` argument.

*Example:* The following command saves 30 frames fetched from a camera capturing the UNIX maze.
```bash
arena-record -i rtsp://10.4.88.15/axis-media/media.amp -o out.mp4 --frame-end 30
```
