from . import arguments
from . import functions
from argparse import ArgumentParser, _SubParsersAction


def add_parsers(parser: _SubParsersAction):
    mainparser: ArgumentParser = parser.add_parser('flow', help='onprem to cloud')
    subparser = mainparser.add_subparsers(dest='command', required=True)
    arguments.test_parser(subparser)
    arguments.download_parser(subparser)
    # arguments.upload_parser(subparser)
    arguments.create_parser(subparser)