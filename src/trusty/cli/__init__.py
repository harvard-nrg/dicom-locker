import logging
from pathlib import Path
from argparse import ArgumentParser
from trusty.server import StorageService
from trusty.commons import catch_exdev, print_platform_info

logger = logging.getLogger(__name__)

def trusty():
    parser = ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=11112)
    parser.add_argument('--maximum-pdu-size', type=int, default=0)
    parser.add_argument('--thread-workers', type=int, default=8)
    parser.add_argument('--incoming', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('-v', '--verbose')
    args = parser.parse_args()

    level = logging.INFO
    if args.verbose:
        debug_logger()
        level = logging.DEBUG
    logging.basicConfig(level=level)

    print_platform_info(args)

    args.incoming.mkdir(parents=True, exist_ok=True)
    args.archive.mkdir(parents=True, exist_ok=True)

    catch_exdev([
        args.archive,
        args.incoming
    ])

    server = StorageService(
        host=args.host,
        port=args.port,
        incoming=args.incoming,
        archive=args.archive,
        maximum_pdu_size=args.maximum_pdu_size,
        thread_workers=args.thread_workers
    )
    server.forever()

