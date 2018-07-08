import os
import struct
import sys


class ttyrec():
    def __init__(self, path):
        self.path = path
        self.frame_count = 0
        self.frame_index = []
        self.epochal_timestamps = True
        self.total_play_time = 0
        self.memory_resident = False
        self.duration_removed = 0
        self.frames_shortened = 0

    def shorten_long_frames(self, max_duration):
        """Make each frame's timestamp in seconds no greater than max_duration"""
        self.memory_resident = True  # We shorten in memory, so become memory resident
        if max_duration < 1:
            sys.stderr.write(
                "shorten_long_frames: max_duration cannot be less than 1. Aborting.")
            return
        for i in range(self.frame_count - 1):
            self.frame_index[i +
                             1][0] = self.frame_timestamp(i + 1) - self.duration_removed
            if self.frame_duration(i) > max_duration:
                self.frames_shortened += 1
                self.duration_removed += self.frame_duration(i) - max_duration
                self.frame_index[i +
                                 1][0] = self.frame_index[i][0] + max_duration
        # Update total play time
        self.total_play_time = self.frame_index[self.frame_count -
                                                1][0] - self.frame_index[0][0]

        # Update headers
        for i in range(self.frame_count):
            pl = self.frame_payload(i)
            self.frame_index[i][4] = struct.pack("<iii", self.frame_timestamp(
                i), self.frame_usecs(i), self.frame_payload_size(i)) + pl

    def write_out(self):
        """Write every raw frame to stdout to produce an output ttyrec"""
        for i in range(self.frame_count):
            sys.stdout.write(self.raw_frame(i))
            sys.stdout.flush()

    def parse(self):
        """Parse the ttyrec file."""
        size = os.stat(self.path).st_size

        fh = open(self.path, "rb")
        current_pos = 0
        while current_pos < size:
            frame_header = fh.read(12)
            timestamp, usecs, length = struct.unpack('<iii', frame_header)
            self.frame_count += 1
            if self.memory_resident:
                payload = fh.read(length)
                self.frame_index.append(
                    [timestamp, usecs, length, current_pos, frame_header + payload])
                current_pos += 12 + length
            else:
                self.frame_index.append(
                    [timestamp, usecs, length, current_pos])
                current_pos += 12 + length
                fh.seek(current_pos)
        if self.frame_index[0][2] > 9000:
            self.epochal_timestamps = True
        else:
            self.epochal_timestamps = False
        self.total_play_time = self.frame_index[self.frame_count -
                                                1][0] - self.frame_index[0][0]
        fh.close()

    def mr_parse(self):
        """Parse the ttyrec file, loading everything into memory for speed."""
        self.memory_resident = True
        self.parse()

    def frame_payload_size(self, frame):
        """Returns the payload size of the specified frame."""
        return self.frame_index[frame][2]

    def frame_timestamp(self, frame):
        """Returns the timestamp of the specified frame."""
        return self.frame_index[frame][0]

    def frame_usecs(self, frame):
        """Returns the microsecond part of the timestamp of the specified frame."""
        return self.frame_index[frame][1]

    def frame_offset(self, frame):
        """Returns the offset, from the beginning of the file, of the specified frame."""
        return self.frame_index[frame][3]

    def frame_payload(self, frame):
        """Returns the specified frame's payload."""
        if self.memory_resident:
            return self.frame_index[frame][4][12:]
        else:
            fh = open(self.path, "rb")
            fh.seek(self.frame_index[frame][3] + 12)
            payload = fh.read(self.frame_index[frame][2])
            fh.close()
            return payload

    def frame_duration(self, frame):
        """Returns the duration of the specified frame, or -1 if the specified frame is the last frame in the file."""
        if frame == self.frame_count - 1:
            return -1
        return self.frame_index[frame + 1][0] - self.frame_index[frame][0]

    def raw_frame(self, frame):
        """Returns the specified frame, header and all."""
        if self.memory_resident:
            return self.frame_index[frame][4]
        else:
            fh = open(self.path, "rb")
            fh.seek(self.frame_index[frame][3])
            frame = fh.read(self.frame_index[frame][2] + 12)
            fh.close()
            return frame
