#!/usr/bin/env python3
"""
Rename file according to their ordering.

Usage: rnsort FILE [...FILES]
    FILES - List of files to be renamed
"""
import math
import os
import sys
from typing import List, Union


def deduce_extension(files: List[str]) -> Union[str, None]:
    """
    Find common extension from given files.

    If there is inconsistent extension, None will be returned.
    """
    if len(files) == 0:
        return None

    (_, ext) = os.path.splitext(files[0])
    for file in files:
        (_, e) = os.path.splitext(file)
        if e != ext:
            return None

    return ext


def main() -> None:
    """Entry point of the script."""
    files = sorted(sys.argv[1:])
    if len(files) <= 1:
        print('At least 2 files is required for bulk rename.')
        sys.exit(1)

    ext = deduce_extension(files)
    if ext is None:
        print('Inconsisten extension. Aborting.')
        sys.exit(1)

    magnitude = math.floor(math.log10(len(files))) + 1
    pad = max(magnitude, 2)
    dest = [str(i).zfill(pad) + ext
            for i in range(1, len(files) + 1)]

    print('Going to rename according:')
    for (old, new) in zip(files, dest):
        print(f'{old} -> {new}')

    print('----- Are you sure? -----')
    res = input('Input [Y] to confirm > ')
    if res.lower() != 'y':
        print('Receive cancel signal.')
        sys.exit(1)

    for (old, new) in zip(files, dest):
        os.rename(old, new)
    print('Done')


if __name__ == '__main__':
    main()

