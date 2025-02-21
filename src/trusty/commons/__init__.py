import os
import sys
import stat
import shutil
import platform
from typing import List
from pathlib import Path
from tabulate import tabulate
from tempfile import NamedTemporaryFile
from trusty.exceptions import NoSpaceError, CrossDeviceError

def print_platform_info(args):
    table = [
        ['Platform', platform.platform()],
        ['Processor', platform.processor()],
        ['Python version', platform.python_version()],
        ['GIL enabled', sys._is_gil_enabled()],
        ['Thread workers', args.thread_workers],
        ['Archive directory', args.archive],
        ['Incoming directory', args.incoming]
    ]
    print(tabulate(table, tablefmt='simple_grid'))

def catch_exdev(paths: List[Path]):
    '''
    Check if paths cross devices
    '''
    devices = set()
    for path in paths:
        stat = os.stat(path)
        devices.add(stat.st_dev)
    if len(devices) > 1:
        raise CrossDeviceError(f'paths cross devices {paths}')

def atomicwrite(path: Path, content: bytes, mode: int | None = 0o0640, 
        group: str | None ='mrimgmt'):
    '''
    Write a file with as much safety as possible by
    writing contents to hidden temporary file, then 
    performing a single atomic rename operation
    '''
    path = path.expanduser()
    if path.exists():
        raise FileExistsError(path)
    try:
        with NamedTemporaryFile(dir=path.parent, prefix='.', 
                delete=False) as fo:
            fo.write(content)
            fo.flush()
            os.fsync(fo.fileno())
        if mode:
            os.chmod(fo.name, mode)
        if group:
            shutil.chown(fo.name, group=group)
        os.rename(fo.name, path)
    except OSError as e:
        if e.errno == errno.ENOSPC:
            raise NoSpaceError(filename) from e
        raise e

