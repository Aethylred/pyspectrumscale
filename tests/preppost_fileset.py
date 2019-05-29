#!/usr/bin/env python
"""
A generic wrapper script to list available filesystems
"""
import json
import sys
from pyspectrumscale.Api import Api
from pyspectrumscale.configuration import CONFIG
from pyspectrumscale.Api._utils import jsonprepreq


def main():
    """
    @brief      This provides a wrapper for the pyspectrumscale module

    @return     { description_of_the_return_value }
    """

    if CONFIG['command'] == 'dumpconfig':
        print(json.dumps(CONFIG, indent=2, sort_keys=True))
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

    if len(CONFIG['filesystem']) > 1:
        sys.exit("Requires only one filesystem specified with --filesystem")

    if not CONFIG['fileset']:
        sys.exit("Requires a fileset specified with --fileset")

    if len(CONFIG['fileset']) > 1:
        sys.exit("Requires only one fileset specified with --fileset")

    if not CONFIG['comment']:
        sys.exit("Requires a comment specified with --comment")

    if not CONFIG['parent']:
        sys.exit("Requires a parent specified with --parent")

    if not CONFIG['path']:
        sys.exit("Requires a path specified with --path")

    response = scaleapi.preppost_fileset(
        filesystem=CONFIG['filesystem'][0],
        fileset=CONFIG['fileset'][0],
        path=CONFIG['path'],
        owner='root',
        group='root',
        permissions='0750',
        permissionchangemode='chmodAndUpdateAcl',
        parent=CONFIG['parent'],
        comment=CONFIG['comment']
    )
    sendresponse = scaleapi.send(response)

    print(json.dumps(jsonprepreq(response), indent=2, sort_keys=True))

    if CONFIG['dryrun']:
        print(json.dumps(sendresponse, indent=2, sort_keys=True))
    else:
        print(json.dumps(sendresponse.json(), indent=2, sort_keys=True))
        jobid = sendresponse.json()['jobs'][0]['jobId']
        jobresponse = scaleapi.jobs(jobid)
        print(json.dumps(jobresponse, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
