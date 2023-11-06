from argparse import _SubParsersAction, ArgumentParser


def create_parser(parser: _SubParsersAction):
    subparser: ArgumentParser = parser.add_parser('create', help='bind airflow or composer')
    subparser.add_argument('-t', '--flowtype', help='flow type', choices=['airflow', 'composer'])
    subparser.add_argument('-n', '--name', help='flow name', required=True)
    subparser.add_argument('-a', '--address', help='airflow home full address on machine', required=True)
    subparser.add_argument('--host', help='host for ftp connection', required=True)
    subparser.add_argument('-u', '--username', help='username for ftp connection', required=True)
    subparser.add_argument('-p', '--password', help='password for ftp connection', required=True)

def test_parser(parser: _SubParsersAction):
    subparser: ArgumentParser = parser.add_parser('test', help='bind airflow or composer')
    subparser.add_argument('-n', '--name', help='flow name', required=True)

def download_parser(parser: _SubParsersAction):
    subparser: ArgumentParser = parser.add_parser('download', help='bind airflow or composer')
    subparser.add_argument('-n', '--name', help='flow name', required=True)

# def upload_parser(parser: _SubParsersAction):
#     subparser: ArgumentParser = parser.add_parser('upload', help='bind airflow or composer')
#     subparser.add_argument('-n', '--name', help='flow name', required=True)