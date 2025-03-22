#!/usr/bin/env python
"""Command line tool to say hello to a user."""

import argparse
import getpass


def main():
    """Run the command-line tool."""
    parser = argparse.ArgumentParser(description='Say hello to a user.')
    parser.add_argument('--name', type=str, default=getpass.getuser(),
                        help='Name of the user to greet (default: current system user)')
    
    args = parser.parse_args()
    print(f"hello {args.name}")


if __name__ == '__main__':
    main() 