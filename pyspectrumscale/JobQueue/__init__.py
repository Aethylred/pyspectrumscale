"""
Create a JobQueue that can manage and track requests sent to
the Spectrum Scale API
"""
import json
from requests import PreparedRequest
from typing import Union
from uuid import uuid4 as uuid
from pyspectrumscale.Api import Api
from pyspectrumscale.Api._utils import jsonprepreq


class JobQueue:
    """
    A JobQueue that can manage and track requests sent to
    the Spectrum Scale API
    """

    def __init__(
        self,
        scaleapi: type=Api
    ):
        self._scalapi = scaleapi
        self._jobs = {}

    def listjobs(
        self,
        asjson: bool=False
    ):

        joblist = dict(self._jobs)
        if asjson:
            for jobuuid in joblist:
                job = self.job(jobuuid, asjson=asjson)
                joblist[jobuuid] = job

        return joblist

    def job(
        self,
        jobuuid: str,
        asjson: bool=False
    ):
        job = dict(self._jobs[jobuuid])

        if asjson:
            job['request'] = jsonprepreq(job['request'])

        return job

    def queuejob(
        self,
        request: type=PreparedRequest,
        requires: Union[str, None]=None
    ):

        response = {
            'queued': False,
            'reasons': [],
            'uuid': None
        }

        # Has the request already been submitted
        duplicates = []
        for jobuuid in self.listjobs():
            if request == self.job(jobuuid)['request']:
                duplicates.append(jobuuid)

        if duplicates:
            for jobuuid in duplicates:
                reason = "Request already queued as a job (ID:%s)" % jobuuid
                response['reasons'].append(reason)

            response['uuid'] = duplicates[0]
        else:
            jobuuid = str(uuid())
            self._jobs[jobuuid] = {
                'request': request,
                'status': 'New',
                'jobid': None,
                'requires': requires
            }
            response['queued'] = True
            response['uuid'] = jobuuid

        return response
