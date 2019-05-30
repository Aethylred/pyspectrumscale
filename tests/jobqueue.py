#!/usr/bin/env python
"""
A generic wrapper script to list available filesystems
"""
import json
import sys
from pyspectrumscale.Api import Api
from pyspectrumscale.JobQueue import JobQueue
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

    jobqueue = JobQueue(scaleapi)

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

    # Prepare the following requests:
    # - create a fileset
    # - set a quota on the fileset
    # - set an ACL on the fileset
    # Quota and ACL require that the first job completes before being submitted
    fspreprequest = scaleapi.preppost_fileset(
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

    quotapreprequest = scaleapi.preppost_quota(
        filesystem=CONFIG['filesystem'][0],
        fileset=CONFIG['fileset'][0],
        blocksoftlimit='10G',
        blockhardlimit='11G',
        blockgraceperiod='7days',
        filessoftlimit='10M',
        fileshardlimit='11M',
        filesgraceperiod='7days',
        quotatype="FILESET"
    )

    aclentries = [
        {
            'flags': '',
            'permissions': 'rwmxDaAnNcCos',
            'type': 'allow',
            'who': 'special:owner@'
        },
        {
            'flags': '',
            'permissions': 'rwmxDancs',
            'type': 'allow',
            'who': 'special:group@'
        },
        {
            'flags': '',
            'permissions': 'rxancs',
            'type': 'allow',
            'who': 'group:apps-team'
        },
        {
            'flags': '',
            'permissions': 'ancs',
            'type': 'allow',
            'who': 'special:everyone@'
        },
        {
            'flags': 'fdi',
            'permissions': 'rwmxDaAnNcCos',
            'type': 'allow',
            'who': 'special:owner@'
        },
        {
            'flags': 'fdi',
            'permissions': 'rwmxDancs',
            'type': 'allow',
            'who': 'special:group@'
        },
        {
            'flags': 'fdi',
            'permissions': 'rxancs',
            'type': 'allow',
            'who': 'group:apps-team'
        },
        {
            'flags': 'fdi',
            'permissions': 'ancs',
            'type': 'allow',
            'who': 'special:everyone@'
        }
    ]

    aclpreprequest = scaleapi.prepput_acl(
        filesystem=CONFIG['filesystem'][0],
        path=CONFIG['path'],
        entries=aclentries
    )

    queueresponse01 = jobqueue.queuejob(fspreprequest)
    queueresponse02 = jobqueue.queuejob(
        request=quotapreprequest,
        runonfail=False,
        requires=queueresponse01['uuid']
    )
    queueresponse03 = jobqueue.queuejob(
        request=aclpreprequest,
        requires=queueresponse01['uuid']
    )

    # print(json.dumps(jsonprepreq(preprequest), indent=2, sort_keys=True))

    # print(json.dumps(queueresponse01, indent=2, sort_keys=True))
    # print('---')
    # print(json.dumps(queueresponse02, indent=2, sort_keys=True))
    # print('---')
    # print(json.dumps(queueresponse03, indent=2, sort_keys=True))
    # print('+++')
    # print(json.dumps(jobqueue.listjobs(asjson=True), indent=2, sort_keys=True))
    # print('---')

    submitresponse = jobqueue.submitjobs()
    print(json.dumps(submitresponse, indent=2, sort_keys=True))
    print('---')
    submitresponse = jobqueue.submitjobs()
    print(json.dumps(submitresponse, indent=2, sort_keys=True))
    print('---')
    print(json.dumps(jobqueue.listjobs(asjson=True), indent=2, sort_keys=True))


    # Test what happens if the job us resubmitted
    # queueresponse01 = jobqueue.queuejob(preprequest)
    # print(json.dumps(queueresponse01, indent=2, sort_keys=True))
    # print(json.dumps(jobqueue.listjobs(asjson=True), indent=2, sort_keys=True))

    # if CONFIG['dryrun']:
    #     print(json.dumps(sendresponse, indent=2, sort_keys=True))
    # else:
    #     print(json.dumps(sendresponse.json(), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
