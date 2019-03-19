"""
Process command line arguments and/or load configuration file
mostly used by the test scripts
"""
import argparse
import sys
import os.path
from typing import Union
import yaml


def do_args():
    """
    @brief      { function_description }

    @return     { description_of_the_return_value }
    """
    # Parse command line arguments and modify config
    parser = argparse.ArgumentParser(
        prog='pyspectrumscale.py',
        description='Python Spectrum Scale Management API tools'
    )

    # Command line arguments
    parser.add_argument(
        "-v",
        "--verbose",
        dest='verbose',
        help="Increase output to stderr and stdout",
        action="store_true"
    )

    parser.add_argument(
        "-q",
        "--quiet",
        dest='quiet',
        help="Reduce output to stderr and stdout",
        action="store_true"
    )

    parser.add_argument(
        "-d",
        "--dry_run",
        dest='dryrun',
        help="Do a dry run, no changes written to Spectrum Scale or GPFS",
        action="store_true"
    )

    parser.add_argument(
        "-f",
        "--file",
        default='pyspectrumsscale.conf.yaml',
        dest='file',
        help="Specify a configuration file, default is pyspectrumsscale.conf.yaml",
    )

    parser.add_argument(
        "--filesystem",
        default=None,
        dest='filesystem',
        help="Specify a scale filesystem",
    )

    parser.add_argument(
        "--fileset",
        default=None,
        dest='fileset',
        help="Specify a scale filesystem, requires a filesystem",
    )

    parser.add_argument(
        '-s',
        '--server',
        default=None,
        type=str,
        dest='server',
        help="Hostname of Spectrum Scale Management server"
    )

    parser.add_argument(
        '-u',
        '--user',
        default=None,
        type=str,
        dest='user',
        help="The username used to connect to the Spectrum Scale Management server"
    )

    parser.add_argument(
        '-p',
        '--password',
        default=None,
        type=str,
        dest='password',
        help="The password used to conenct to the Spectrum Scale Management server"
    )

    parser.add_argument(
        '--port',
        default=None,
        type=str,
        dest='port',
        help="The password used to conenct to the Spectrum Scale Management server"
    )

    parser.add_argument(
        '--version',
        default=None,
        type=str,
        dest='version',
        help="The Spectrum Scale Management server API version"
    )

    parser.add_argument(
        '--verify_ssl',
        default=None,
        type=bool,
        dest='verify_ssl',
        help=(
            "If true the SSL certificate of the"
            " Spectrum Scale Management server will be verified"
        )
    )

    parser.add_argument(
        '--verify_warnings',
        default=None,
        type=bool,
        dest='verify_warnings',
        help=(
            "If false warnings about the SSL state of "
            "the Spectrum Scale Management server will be silenced"
        )
    )

    parser.add_argument(
        '--verify_method',
        default=None,
        type=Union[bool, str],
        dest='verify_method',
        help=(
            "The method used to validate the SSL state of "
            "the Spectrum Scale Management server"
        )
    )

    # Positional commands
    parser.add_argument(
        dest='command',
        help='Command help',
        default=None,
        nargs='?',
        type=str,
        choices=[
            'dumpconfig',
            'connectiontest'
        ]
    )

    return parser.parse_args()

# Create the CONFIG to be imported elsewhere
# Set defaults
CONFIG = {
    'scaleserver': {
        'host': 'scaleserver.example.org',
        'user': 'username',
        'password': None,
        'port': 443,
        'version': 'v2',
        'verify_ssl': True,
        'verify_method': True,
        'verify_warnings': True
    },
}


ARGS = do_args()

# Override configuration defaults with values from the config file
if os.path.isfile(ARGS.file):
    with open(ARGS.file, 'r') as configfile:
        CONFIG.update(yaml.load(configfile))

# Override configuration loaded from file with command line arguments
if ARGS.server:
    CONFIG['scaleserver']['host'] = ARGS.server

if ARGS.user:
    CONFIG['scaleserver']['user'] = ARGS.user

if ARGS.password:
    CONFIG['scaleserver']['password'] = ARGS.password

if ARGS.port:
    CONFIG['scaleserver']['port'] = ARGS.port

if ARGS.version:
    CONFIG['scaleserver']['version'] = ARGS.version

# This one can be bool or str values
if ARGS.verify_method is not None:
    CONFIG['scaleserver']['verify_method'] = ARGS.verify_method

if ARGS.verify_ssl is not None:
    CONFIG['scaleserver']['verify_ssl'] = ARGS.verify_ssl

if ARGS.verify_warnings is not None:
    CONFIG['scaleserver']['verify_warnings'] = ARGS.verify_warnings

# If there's no config file, write one
if not os.path.isfile(ARGS.file):
    print(
        "The configuration file %s was missing,"
        " wrote default configuration to file" %
        ARGS.file
    )
    with open(ARGS.file, 'w') as configfile:
        yaml.dump(CONFIG, configfile, default_flow_style=False)
    sys.exit(0)

# Set state from command line
CONFIG['command'] = ARGS.command
CONFIG['dryrun'] = ARGS.dryrun
CONFIG['filesystem'] = ARGS.filesystem
CONFIG['fileset'] = ARGS.fileset
