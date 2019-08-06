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
        self.EMPTY = 'EMPTY'
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
            self.EMPTY,
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
        job = None

        if jobuuid in self._jobs:
            job = dict(self._jobs[jobuuid])

            if asjson:
                job['request'] = jsonprepreq(job['request'])

            # If we're asking about a job, update it's status
            if job['status'] in self.RUNNINGSTATES and job['jobid']:
                jobresponse = self._scaleapi.job(job['jobid'])
                newstatus = jobresponse['status']
                job['status'] = newstatus
                self._jobs[jobuuid]['status'] = newstatus
                if newstatus in self.FAILEDSTATES:
                    errormsg = jobresponse['result']['stderr'][0]
                    job['ok'] = False
                    job['error'] = errormsg
                    self._jobs[jobuuid]['ok'] = False
                    self._jobs[jobuuid]['error'] = errormsg

        return job

    def jobstatus(
            self,
            jobuuids: Union[str, None]=None,
    ):
        """
        """
        response = {}
        if isinstance(jobuuids, list):
            for jobuuid in jobuuids:
                job = self.job(jobuuid)
                if job is not None:
                    jobstatus = {
                        'ok': job['ok'],
                        'status': job['status']
                    }
                    if 'error' in job:
                        jobstatus['error'] = job['error']
                    response[jobuuid] = jobstatus
        elif jobuuids is not None:
            job = self.job(jobuuids)
            if job is not None:
                jobstatus = {
                    'ok': job['ok'],
                    'status': job['status']
                }
                if 'error' in job:
                    jobstatus['error'] = job['error']
                response[jobuuid] = jobstatus
        else:
            for jobuuid in self.listjobuuids():
                job = self.job(jobuuid)
                if job is not None:
                    jobstatus = {
                        'ok': job['ok'],
                        'status': job['status']
                    }
                    if 'error' in job:
                        jobstatus['error'] = job['error']
                    response[jobuuid] = jobstatus

        return response

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

    def status(self):
        """
        """

        status = {
            'status': self.EMPTY,
            'jobcount': 0,
            'failcount': 0,
            'newcount': 0,
            'runningcount': 0,
            'completecount': 0,
            'failreports': {}
        }
        jobstatus = self.jobstatus()
        status['jobcount'] = len(jobstatus)
        if status['jobcount'] > 0:
            status['status'] = self.PENDING

        for jobuuid, state in jobstatus.items():
            if state['status'] in self.COMPLETEDSTATES:
                status['completecount'] += 1
                if state['status'] in self.FAILEDSTATES:
                    status['failcount'] += 1
                    status['failreports'][jobuuid] = state['error']
            elif state['status'] in self.RUNNINGSTATES:
                status['runningcount'] += 1
            else:
                status['newcount'] += 1

        if status['runningcount']:
            status['status'] = self.RUNNING
        elif status['completecount']:
            status['status'] = self.COMPLETED

        return status


## WARNING: The following methods can make requests that can make changes
## on the Spectrum Scale filesystem

    def submitjobs(self):
        """
        @brief      This is a single submission iteration of the JobQueue

        @param      self  The JobQueue object

        @return     a list of dict responses from each of the jobs submitted
        """

        response = {}
        for jobuuid in self._jobs:
            newsubmission = False
            requireuuid = None
            requirestatus = None
            if self._jobs[jobuuid]['ok']:
                if self._jobs[jobuuid]['status'] in self.NEWSTATES:
                    requireuuid = self.job(jobuuid)['requires']
                    if requireuuid:
                        requiredjob = self.job(requireuuid)
                        requirestatus = requiredjob['status']
                        if requirestatus in self.COMPLETEDSTATES:
                            if requirestatus in self.FAILEDSTATES:
                                if self.job(jobuuid)['runonfail']:
                                    newsubmission = True
                                else:
                                    self._jobs[jobuuid]['status'] = self.REQUIREDFAILED
                                    self._jobs[jobuuid]['error'] = (
                                        "Required job %s failed" %
                                        self.job(jobuuid)['requires']
                                    )
                                    self._jobs[jobuuid]['ok'] = False
                        else:
                            self._jobs[jobuuid]['status'] = self.PENDING
                    else:
                        newsubmission = True
                elif self._jobs[jobuuid]['status'] in self.RUNNINGSTATES:
                    # This will refresh the job status of a running job
                    self.job(jobuuid)

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
                'requires': requireuuid,
                'requirestatus': requirestatus,
                'newsubmission': newsubmission
            }

        return response

    def run(
        self,
        completelog: bool=False,
        tick: bool=False
    ):
        """
        @brief      { function_description }

        @param      self  The object

        @return     { description_of_the_return_value }
        """

        response = None
        if completelog:
            response = []

        if self._scaleapi._dryrun:
            # Do one submit
            if tick:
                print('-')
            response = self.submitjobs()

        else:
            # Run until completed
            while self.status()['status'] not in self.COMPLETEDSTATES:
                if tick:
                    print('.', end="")
                submitresponse = self.submitjobs()
                if completelog:
                    response.append(submitresponse)
                else:
                    response = submitresponse

            if tick:
                print("!")

        if isinstance(response, list):
            if len(response) == 1:
                response = response[0]

        return response
