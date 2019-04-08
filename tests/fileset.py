#!/usr/bin/env python
"""
A generic wrapper script to list available filesystems
"""
import json
import sys
from pyspectrumscale.Api import Api
from pyspectrumscale.configuration import CONFIG


def main():
    """
    @brief      This provides a wrapper for the pyspectrumscale module

    @return     { description_of_the_return_value }
    """

    if CONFIG['command'] == 'dumpconfig':
        print(json.dumps(CONFIG, indent=4, sort_keys=True))
        sys.exit(0)

    # Define API session
    scaleapi = Api(
        host=CONFIG['scaleserver']['host'],
        username=CONFIG['scaleserver']['user'],
        password=CONFIG['scaleserver']['password'],
        port=CONFIG['scaleserver']['port'],
        verify_ssl=CONFIG['scaleserver']['verify_ssl'],
        verify_method=CONFIG['scaleserver']['verify_method'],
        verify_warnings=CONFIG['scaleserver']['verify_warnings'],
        dryrun=CONFIG['dryrun']
    )

    if not CONFIG['filesystem']:
        sys.exit("Requires a filesystem specified with --filesystem")

    if CONFIG['fileset']:
        response = scaleapi.fileset(
            CONFIG['filesystem'],
            CONFIG['fileset']
        )
    else:
        response = scaleapi.fileset(
            CONFIG['filesystem']
        )

    print(json.dumps(response.json(), indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
