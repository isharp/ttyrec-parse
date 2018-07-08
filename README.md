# ttyrec-parse
Simple parser for ttyrec files. Capable of shortening long frames to specified duration.

Usage:

```python
from ttyrec import ttyrec

testrec = ttyrec('test.ttyrec')
testrec.mr_parse() # memory resident parse, for non-mr, call parse()
print("Total frames: {}".format(testrec.frame_count))
print("Total duration: {}s".format(testrec.total_play_time))
print("Shortening long frames.")
testrec.shorten_long_frames(2)
print("Shortened {} frames.".format(testrec.frames_shortened))
print("New total duration: {}".format(testrec.total_play_time))
# Write shortened ttyrec to stdout
# testrec.write_out()

```
