import argparse

# applications
import flows

applications = [
    flows,
]

if __name__  == '__main__':
    parser = argparse.ArgumentParser(
        prog = 'turboflow',
        description = '',
        epilog = '')
    
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Creating command set
    commands_map = {}
    for app in applications:
        commands_map.update(app.commands_map)
        app.add_parsers(subparsers)


    args = parser.parse_args()

    func = commands_map[args.command]
    func(**vars(args))