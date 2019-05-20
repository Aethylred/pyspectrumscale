"""
A generic wrapper for the pyspectrumscale Api class
"""
import json
import sys
from pyspectrumscale.Api import Api
from pyspectrumscale.configuration import CONFIG


def main():
    """
    @brief      This provides a wrapper for the pyfreeipa module

    @return     Returns a configured and ready to use pyspectrumscale.Api object
    """

    if CONFIG['command'] == 'dumpconfig':
        print(json.dumps(CONFIG, indent=2, sort_keys=True))
        sys.exit(0)

    # Define API Session
    scaleapi = Api(
        host=CONFIG['scaleserver']['host'],
        username=CONFIG['scaleserver']['user'],
        password=CONFIG['scaleserver']['password'],
        port=CONFIG['scaleserver']['port'],
        verify_ssl=CONFIG['scaleserver']['verify_ssl'],
        verify_method=CONFIG['scaleserver']['verify_method'],
        verify_warnings=CONFIG['scaleserver']['verify_warnings'],
        version=CONFIG['scaleserver']['version'],
        dryrun=CONFIG['dryrun']
    )

    if CONFIG['command'] == 'connectiontest':
        print(
            "Test connection to %s" %
            CONFIG['scaleserver']['host']
        )

        response = scaleapi.info()
        if response.ok:
            print(
                'Successfully connected to as %s on %s' %
                (
                    CONFIG['scaleserver']['user'],
                    CONFIG['scaleserver']['host']
                )
            )
            result = response.json()
            print(result)
        else:
            print(
                'Failed to get info as %s in to %s from %s, reason "%s: %s"' %
                (
                    CONFIG['scaleserver']['user'],
                    CONFIG['scaleserver']['host'],
                    response.url,
                    response.status_code,
                    response.reason
                )
            )

    else:
        print("No command provided")


if __name__ == "__main__":
    main()
