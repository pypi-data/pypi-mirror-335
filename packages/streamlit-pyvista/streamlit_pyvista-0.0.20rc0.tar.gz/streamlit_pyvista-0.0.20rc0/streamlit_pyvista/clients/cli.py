import argparse
import sys
from ..proxy import launch_proxy


def run_proxy():
    launch_proxy()


def main():
    parser = argparse.ArgumentParser(description="Streamlit-PyVista CLI")
    parser.add_argument('command', choices=['run'])
    parser.add_argument('subcommand', choices=['proxy'])

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.command == 'run':
        if args.subcommand == 'proxy':
            run_proxy()


if __name__ == "__main__":
    main()
