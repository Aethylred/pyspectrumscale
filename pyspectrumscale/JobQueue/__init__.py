"""
Create a JobQueue that can manage and track requests sent to
the Spectrum Scale API
"""
import json
from requests import PreparedRequest, Response
from typing import Union
from uuid import uuid4 as uuid
from pyspectrumscale.Api import Api
from pyspectrumscale.Api._utils import jsonprepreq, jsonresponse


class JobQueue:
    """
    A JobQueue that can manage and track requests sent to
    the Spectrum Scale API
    """

    def __init__(
        self,
        scaleapi: type=Api
    ):
        self._scaleapi = scaleapi
        self._jobs = {}

        # Globals:
        self.NEW = 'NEW'
        self.PENDING = 'PENDING'
        self.SUBMITTED = 'SUBMITTED'
        self.SUBMITFAILED = 'SUBMITFAILED'
        self.REQUIREDFAILED = 'REQUIREDFAILED'
        self.RUNNING = 'RUNNING'
        self.COMPLETED = 'COMPLETED'
        self.FAILED = 'FAILED'
        self.NEWSTATES = [
            self.NEW,
            self.PENDING
        ]
        self.SUBMITTEDSTATES = [
            self.SUBMITTED,
            self.SUBMITFAILED,
            self.RUNNING,
            self.COMPLETED,
            self.FAILED
        ]
        self.RUNNINGSTATES = [self.SUBMITTED, self.RUNNING]
        self.COMPLETEDSTATES = [
            self.COMPLETED,
            self.SUBMITFAILED,
            self.FAILED,
            self.REQUIREDFAILED
        ]
        self.SUCCESSSTATES = [self.COMPLETED]
        self.FAILEDSTATES = [
            self.SUBMITFAILED,
            self.REQUIREDFAILED,
            self.FAILED
        ]

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

    def listjobuuids(
        self
    ):
        idlist = []
        for jobuuid in self.listjobs():
            idlist.append(jobuuid)

        return idlist

    def listjobids(
        self
    ):
        idlist = []
        for jobuuid in self.listjobs():
            idlist.append(self.job(jobuuid)['jobid'])

        return idlist

    def job(
        self,
        jobuuid: str,
        asjson: bool=False
    ):
        job = dict(self._jobs[jobuuid])

        if asjson:
            job['request'] = jsonprepreq(job['request'])

        # If we're asking about a job, update it's status
        if job['status'] in self.RUNNINGSTATES and job['jobid']:
            newstatus = self._scaleapi.job(job['jobid'])['status']
            job['status'] = newstatus
            self._jobs[jobuuid]['status'] = newstatus
            if newstatus in self.FAILEDSTATES:
                job['ok'] = False
                self._jobs[jobuuid]['ok'] = False

        return job

    def queuejob(
            self,
            request: type=PreparedRequest,
            requires: Union[str, None]=None,
            runonfail: bool=True
    ):
        """
        @brief      Add a job to the job queue

        @param      self       This JobQueue object
        @param      request    A requests.PreparedRequest object to submit to the Spectrum Scale API
        @param      requires   The uuid of a job that needs to finishe before this job runs
        @param      runonfail  If true this job will run if a required job is COMPLETE or FAIELD, if false it will only run if a required job is COMPLETED

        @return     { description_of_the_return_value }
        """

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
                'status': self.NEW,
                'jobid': None,
                'sendresponse': None,
                'requires': requires,
                'runonfail': runonfail,
                'ok': True
            }
            response['queued'] = True
            response['uuid'] = jobuuid

        return response

    def submitjobs(self):

        response = {}
        for jobuuid in self._jobs:
            newsubmission = False
            if self._jobs[jobuuid]['ok']:
                if self._jobs[jobuuid]['status'] in self.NEWSTATES:
                    requireduuid = self.job(jobuuid)['requires']
                    if requireduuid:
                        requiredjob = self.job(requireduuid)
                        if requiredjob['status'] in self.COMPLETEDSTATES:
                            if not (requiredjob['status'] in self.FAILEDSTATES and not self.job(jobuuid)['runonfail']):
                                newsubmission = True
                            else:
                                self._jobs[jobuuid]['status'] = self.REQUIREDFAILED
                        else:
                            self._jobs[jobuuid]['status'] = self.PENDING

                    else:
                        newsubmission = True

            if newsubmission:
                sendresponse = self._scaleapi.send(self._jobs[jobuuid]['request'])
                if isinstance(sendresponse, Response):
                    # self._jobs[jobuuid]['sendresponse'] = sendresponse.json()
                    if sendresponse.ok:
                        self._jobs[jobuuid]['sendresponse'] = sendresponse.json()
                        self._jobs[jobuuid]['status'] = self.SUBMITTED
                        if 'jobs' in sendresponse.json():
                            self._jobs[jobuuid]['jobid'] = sendresponse.json()['jobs'][0]['jobId']
                    else:
                        self._jobs[jobuuid]['sendresponse'] = jsonresponse(sendresponse)
                        self._jobs[jobuuid]['status'] = self.SUBMITFAILED
                        self._jobs[jobuuid]['ok'] = False
                else:
                    # This is likely because of dryrun
                    self._jobs[jobuuid]['sendresponse'] = sendresponse

            response[jobuuid] = {
                'status': self._jobs[jobuuid]['status'],
                'ok': self._jobs[jobuuid]['ok'],
                'jobid': self._jobs[jobuuid]['jobid'],
                'newsubmission': newsubmission
            }

        return response
