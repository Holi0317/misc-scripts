#!/usr/bin/env python3
"""
Watch clipboard and append new content to a file.

Usage:
    clipman FILE
    FILE - File to output to
"""
import sys
import subprocess
import logging
import time
from typing import Generator, List

logger = logging.getLogger(__name__)


def get_path(argv: List[str]) -> str:
    """
    Parse argument and get destination file.

    Raise:
        ValueError - Destination file is not given.
    """
    if len(argv) < 2:
        raise ValueError('Destination file not given')

    dest = argv[1]

    return dest


def poll_clipboard() -> Generator[str, None, None]:
    """
    Get input from clipboard.

    If clipboard content did not change or content is empty,
    this will not yield.

    At least 1 second will be waited for each check.
    """
    buf = ''

    while True:
        process = subprocess.run(['xclip', '-o'],
                                 stdout=subprocess.PIPE, check=True)
        out = process.stdout.decode()
        logger.debug('Got clipboard output: %s', out)
        if out != buf:
            buf = out
            logger.debug('Clipboard content changed.')
            yield out
        time.sleep(1)


def append_file(filepath: str, content: str) -> None:
    """Append content to file."""
    logger.info('Appending to file: %s, "%s"', filepath, content)
    with open(filepath, 'a') as file:
        file.write(content)


def main() -> None:
    """Entry point of the script."""
    # Set up logger
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s / %(levelname)s] %(message)s',
        '%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    dest = get_path(sys.argv)

    for text in poll_clipboard():
        append_file(dest, text)


if __name__ == '__main__':
    main()

