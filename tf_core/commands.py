import argparse
import importlib
from . import IApp


def run(applications):
    parser = argparse.ArgumentParser(
        prog = 'turboflow',
        description = '',
        epilog = '')
    
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Creating command set
    commands_map = {}
    for app_str in applications:
        app: IApp = importlib.import_module(app_str)
        commands_map.update(app.commands_map)
        app.add_parsers(subparsers)


    args = parser.parse_args()

    func = commands_map[args.command]
    func(**vars(args))