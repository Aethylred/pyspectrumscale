"""
Methods for pyspectrumscale.Api that deal with jobs running on the Scale server
"""
from typing import Union


def get_jobs(
        self,
        jobid: Union[str, None]=None
):
    """
    @brief      Gets the job.

    @param      self   The object
    @param      jobid  The jobid

    @return     The job.
    """

    if jobid is not None:
        commandurl = "%s/jobs/%s" % (
            self._baseurl,
            jobid
        )
    else:
        commandurl = "%s/jobs" % (
            self._baseurl
        )

    return self._get(commandurl)


def job(
        self,
        jobid: str
):
    response = None

    jobresponse = self.get_jobs(jobid)

    if jobresponse.ok:
        response = jobresponse.json()['jobs']
        if len(response) == 1:
            response = response[0]

    return response


def jobs(
        self,
        jobids: Union[str, None]=None
):
    response = []

    if jobids is None:
        jobresponse = self.get_jobs()
        if jobresponse.ok:
            response = jobresponse.json()['jobs']
            if len(response) == 1:
                response = response[0]
    elif isinstance(jobids, list):
        for jobid in jobids:
            jobresponse = self.job(jobid)
            if isinstance(jobresponse, list):
                response += jobresponse
            else:
                if jobresponse is not None:
                    response.append(jobresponse)
    else:
        jobresponse = self.job(jobids)
        if isinstance(jobresponse, list):
            response += jobresponse
        else:
            if jobresponse is not None:
                response.append(jobresponse)

    if isinstance(response, list):
        if len(response) == 1:
            response = response[0]

    if not response:
        response = None

    return response


def list_jobs(
        self,
        jobids: Union[str, None]=None
):

    response = []

    jobs = self.jobs(jobids)

    for job in jobs:
        response.append(job['jobId'])

    return sorted(set(response))
