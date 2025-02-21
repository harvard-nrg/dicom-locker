import os
import errno
import logging
import pydicom
from uuid import uuid4
from pathlib import Path
from trusty.sorter import Sorter
from argparse import ArgumentParser
from trusty.commons import atomicwrite
from trusty.exceptions import NoSpaceError
from concurrent.futures import ThreadPoolExecutor
from pynetdicom import (
    AE,
    evt,
    _config,
    debug_logger,
    AllStoragePresentationContexts
)

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, host, port, incoming, archive,
            maximum_pdu_size=0, thread_workers=2):
        self._host = host
        self._port = port
        self._incoming = incoming
        self._archive = archive
        self._ae = AE()
        self._ae.maximum_pdu_size = maximum_pdu_size
        self._ae.supported_contexts = AllStoragePresentationContexts
        self._pool = ThreadPoolExecutor(max_workers=thread_workers)
        _config.UNRESTRICTED_STORAGE_SERVICE = True

    def _rename(self, dcmfile):
        logger.info(f'launching sorter for {dcmfile}')
        sorter = Sorter(dcmfile, self._archive)
        self._pool.submit(sorter.sort)

    def forever(self):
        handlers = [(
            evt.EVT_C_STORE,
            handle_store,
            (
                self,
                self._incoming,
                self._archive
            )
        )]
        logger.info(f'starting storage server {self._host}:{self._port}')
        self._ae.start_server(
            (
                self._host,
                self._port
            ),
            evt_handlers=handlers
        )

def handle_store(event, server, incoming, archive):
    try:
        uuid = str(uuid4())
        filename = incoming / f'{uuid}.dcm'
        atomicwrite(filename, event.encoded_dataset())
    except PermissionError as e:
        logger.exception(e)
        return 0xA700
    except FileExistsError as e:
        logger.exception(e)
        return 0xA700
    except NoSpaceError as e:
        logger.exception(e)
        return 0xA700
    except Exception as e:
        logger.exception(e)
        return 0xC000

    logger.info(f'file was written {filename}')
    server._rename(filename)
    return 0x0000

