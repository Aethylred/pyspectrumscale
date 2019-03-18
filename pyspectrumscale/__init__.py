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

if __name__ == "__main__":
    main()
