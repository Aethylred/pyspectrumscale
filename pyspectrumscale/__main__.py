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
        print(json.dumps(CONFIG, indent=4, sort_keys=True))
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
            CONFIG['ipaserver']['host']
        )

        response = scaleapi.info()
        if response.ok:
            print(
                'Successfully pinged as %s on %s' %
                (
                    CONFIG['ipaserver']['user'],
                    CONFIG['ipaserver']['host']
                )
            )
            result = response.json()['result']
            print(result['summary'])
        else:
            print(
                'Failed to ping as %s in to %s, reason "%s: %s"' %
                (
                    CONFIG['ipaserver']['user'],
                    CONFIG['ipaserver']['host'],
                    response.status_code,
                    response.reason
                )
            )

    else:
        print("No command provided")


if __name__ == "__main__":
    main()
