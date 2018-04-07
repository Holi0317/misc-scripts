#!/usr/bin/env python3
"""
Split video using ffmpeg.

Usage: split.py <FILE> [CFG] [DEST]
    FILE - Source file name. Required argument.
    CFG - Configuration file path. Default: `config`
    DEST - Destination directory. Default: `export/`

Configuration file format:
    Use new line to separate video segments.
    On each line, expected tokens are:

    <START_TIME> <END_TIME> [PREFIX]

    Where time has the following format:
    HH:MM:SS
    (Larger unit could be omitted if they are 00)

    Prefix token is optional.

    Empty line would be skipped. But comment is not supported.

    Output file name would be:
    {prefix}{original-filename}{0-based-index}
"""
import sys
import subprocess
import os
import datetime
from typing import List, Tuple


Config = List[Tuple[datetime.time, datetime.time, str]]


def parse_time(t: str) -> datetime.time:
    """
    Parse timestamps into time object.

    Expected format is HH:MM:SS or MM:SS or SS.
    If the segment starts with 0, for example, 01, the 0 could
    be omitted.

    >>> parse_time('10')
    datetime.time(0, 0, 10)

    >>> parse_time('3:12')
    datetime.time(0, 3, 12)

    >>> parse_time('2:12:05')
    datetime.time(2, 12, 5)
    """
    segment = t.split(':')
    assert len(segment) <= 3, 'Malformed time format'

    if len(segment) == 1:
        s = int(segment[0])
        return datetime.time(0, 0, s)
    if len(segment) == 2:
        m = int(segment[0])
        s = int(segment[1])
        return datetime.time(0, m, s)
    h = int(segment[0])
    m = int(segment[1])
    s = int(segment[2])
    return datetime.time(h, m, s)


def t_to_td(t: datetime.time) -> datetime.timedelta:
    """Convert time to timedelta object."""
    return datetime.timedelta(hours=t.hour,
                              minutes=t.minute,
                              seconds=t.second,
                              microseconds=t.microsecond)


def delta_time(t1: datetime.time, t2: datetime.time) -> datetime.time:
    """Calculate difference in time."""
    dt1 = t_to_td(t1)
    dt2 = t_to_td(t2)
    timedelta = abs(dt2 - dt1)

    hours, rem = divmod(timedelta.total_seconds(), 60 * 60)
    minutes, rem = divmod(rem, 60)
    seconds = rem

    assert hours <= 24, 'Time is too large'

    return datetime.time(round(hours), round(minutes), round(seconds))


def parse_cfg(cfg: str) -> Config:
    """
    Parse configuration file.

    Args:
        cfg - Content of configuration file
    """
    res = []
    for config in cfg.split('\n'):
        if config.strip() == '':
            continue
        times = config.split(' ')

        assert len(times) == 2 or len(times) == 3, 'There should be '
        '2 or 3 time values on each config row'

        if len(times) == 2:
            prefix = ''
        else:
            prefix = times[2] + '-'

        tup = (parse_time(times[0]), parse_time(times[1]), prefix)
        res.append(tup)
    return res


def get_dest_name(src: str, i: int, dest: str, prefix: str) -> str:
    """
    Format for destination file filename.

    Args:
        src - Source filename
        i - Index of current file
        dest - Destination directory
        prefix - Prefix for this file
    """
    index = str(i).zfill(2)
    filename = os.path.split(src)[-1]
    name, ext = os.path.splitext(filename)

    return os.path.join(dest, f'{prefix}{name}-{index}{ext}')


def consutruct_commands(src: str, cfg: Config, dest: str) -> List[List[str]]:
    """
    Construct ffmpeg commands for conversion.

    Arguments:
        src - Path point to source video file
        cfg - Parsed content of configuration file
        dest - Destination directory
    """
    # ffmpeg -ss {start} -i {src} -to {delta} -c copy {dest}
    res = []
    for (i, config) in enumerate(cfg):
        start = config[0]
        end = config[1]
        delta = delta_time(start, end)
        prefix = config[2]
        dest_file = get_dest_name(src, i, dest, prefix)
        res.append(['ffmpeg',
                    '-ss', start.isoformat(),
                    '-i', src,
                    '-to', delta.isoformat(),
                    '-c', 'copy',
                    dest_file])
    return res


def format_cmd(cmd: List[List[str]]) -> str:
    """Format commands for reading."""
    res = []
    for c in cmd:
        res.append(' '.join(c))
    return '\n'.join(res)


def main():
    """Entry point of the script."""
    args = iter(sys.argv)
    next(args)  # First argument is script path

    try:
        src = next(args)
    except StopIteration:
        print('Required argument <config> is not given', file=sys.stderr)
        sys.exit(1)

    conf_path = next(args, 'config')
    dest = next(args, 'export')

    with open(conf_path) as file:
        cfg = parse_cfg(file.read())
    cmd = consutruct_commands(src, cfg, dest)

    print(f'Going to execute the following commands:\n{format_cmd(cmd)}')

    for c in cmd:
        subprocess.run(c)


if __name__ == '__main__':
    main()
