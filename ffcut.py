#!/usr/bin/env python3
"""
Cut multiple segments of one video and combine into one file.

Requires ffmpeg and ffprobe commands in system to work.

Usage: ffcut <FILE> [CONFIG] [OUTPUT]
    FILE - Source file. Required argument.
    CONFIG - Configuration file path. Default: `config`
    OUTPUT - Output directory. Default: `export/`

Configuration file format:
    Use new line to separate video segments.
    On each line, expected tokens are:

    <START_TIME> <END_TIME>

    Where time has the following format:
    HH:MM:SS
    (Larger unit could be omitted if they are 00)

    Empty line would be skipped. But comment is not supported.

Remarks:
    This tool assume existence of nvenc (Nvidia GPU) for hardware-accelrated
    encoding.
    To change this behavior, edit return array from `parse_cfg` function.
"""
import json
import os
import subprocess
import sys
from typing import List, Tuple

Config = List[Tuple[int, int]]


def parse_cfg(cfgpath: str) -> Config:
    """
    Parse configuration file.

    Args:
        cfgpath - Configuration file path

    Returns:
        List of segments. Each item is a tuple of (start_time, end_time)
    """
    res = []

    with open(cfgpath) as file:
        iterator = filter(lambda x: x.strip() != '', file)
        for row in iterator:
            splitted = row.split(' ')
            assert len(splitted) == 2, 'A video segment is malformed'

            start = parse_time(splitted[0])
            end = parse_time(splitted[1])

            assert end > start, 'One segment has smaller end time'
            'than start time!'

            res.append((start, end))

    return res


def build_filter(cfg: Config) -> str:
    """Construct ffmpeg filter using given config."""
    res = []

    for (i, segment) in enumerate(cfg):
        (start, end) = segment
        res += [
            f"[0:v]trim={start}:{end},setpts=PTS-STARTPTS[v{i}];",
            f"[0:a]atrim={start}:{end},asetpts=PTS-STARTPTS[a{i}];"
        ]

    count = round(len(res) / 2)
    streams_id = ''.join([f'[v{i}][a{i}]' for i in range(count)])
    res.append(f'{streams_id}concat=n={count}:v=1:a=1[out]')

    return ''.join(res)


def build_cmd(src: str, cfg: Config, dest: str) -> List[str]:
    """Construct ffmpeg command for conversion."""
    filterarg = build_filter(cfg)
    bitrate = get_bitrate(src) - 128000

    filename = os.path.split(src)[-1]
    output = os.path.join(dest, filename)
    name, _ = os.path.splitext(output)

    return [
        'ffmpeg', '-i', src, '-filter_complex', ''.join(filterarg), '-map',
        '[out]', '-c:v', 'h264_nvenc', '-b:v',
        str(bitrate), name + '.mp4'
    ]


def parse_time(t: str) -> int:
    """
    Parse timestamps into seconds.

    Expected format is HH:MM:SS or MM:SS or SS.
    If the segment starts with 0, for example, 01, the 0 could
    be omitted.

    >>> parse_time('10')
    10

    >>> parse_time('3:12')
    192

    >>> parse_time('2:12:05')
    7925
    """
    segment = t.split(':')
    assert len(segment) <= 3, 'Malformed time format'

    if len(segment) == 1:
        return int(segment[0])
    if len(segment) == 2:
        m = int(segment[0])
        s = int(segment[1])
        return m * 60 + s
    h = int(segment[0])
    m = int(segment[1])
    s = int(segment[2])
    return h * 3600 + m * 60 + s


def get_bitrate(video: str) -> int:
    """
    Interpret given video bitrate using `ffprobe`.

    Note: The returned value is an approximation, rounded down bitrate
    of video.
    """
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
        video
    ]
    process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
    res = json.loads(process.stdout.decode())
    bitrate = res['format']['bit_rate']
    return int(bitrate)


def main() -> None:
    """Entry point of the script."""
    args = iter(sys.argv)
    next(args)  # First argument is script path

    try:
        src = next(args)
    except StopIteration:
        print('Required argument <file> is not given', file=sys.stderr)
        sys.exit(1)

    conf_path = next(args, 'config')
    dest = next(args, 'export')

    cfg = parse_cfg(conf_path)

    if len(cfg) == 0:
        print('Received empty configuration file. Aborting', file=sys.stderr)
        sys.exit(1)

    cmd = build_cmd(src, cfg, dest)

    print('Going to execute the following commands:\n{}'.format(' '.join(cmd)))

    subprocess.run(cmd)


if __name__ == '__main__':
    main()
