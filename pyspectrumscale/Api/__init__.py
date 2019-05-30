"""
Create an Api object that can communicate with the
Spectrum Scale Management API
"""
import json
from typing import Union
import requests
import urllib3
from ._utils import jsonprepreq

class Api:
    """
    @brief     Class to connect to the Spectrum Scale Management API
    """

    from ._filesystem import (
        get_filesystem,
        filesystem,
        filesystems,
        list_filesystems
    )
    from ._fileset import (
        get_fileset,
        fileset,
        filesets,
        list_filesets,
        preppost_fileset
    )
    from ._acl import (
        get_acl,
        acl,
        acls,
        list_acls,
        prepput_acl
    )
    from ._quota import (
        get_quota,
        quota,
        quotas,
        preppost_quota
    )
    from ._job import (
        get_jobs,
        job,
        jobs,
        list_jobs
    )

    def __init__(
            self,
            host: type=str,
            username: type=str,
            password: type=str,
            port: int=443,
            protocol: str='https',
            verify_ssl: bool=True,
            verify_method: Union[bool, str]=True,
            verify_warnings: bool=True,
            version: str='v2',
            dryrun: bool=False
    ):
        """
        @brief      Initiator of the pyspectrumscale.Api class

        @param      self             The object
        @param      host             The spectrum scale management server
        @param      username         The username used to connect to the spectrum scale management server
        @param      password         The password used to authenticate the username
        @param      port             The port used to connect to the spectrum scale management server
        @param      protocol         The protocol used to connect to the spectrum scale management server
        @param      verify_ssl       If true the connection will verifiy SSL
        @param      verify_method    If true this specifies the method used to verify SSL
        @param      verify_warnings  If false SSL verification warnings will be suppress
        @param      version          The Spectrum Scale Management API version
        @param      dryrun           If true, the API will not write changes to Spectrum Scale or GPFS
        """

        self._host = host
        self._username = username
        self._password = password
        self._port = port
        self._protocol = protocol
        self._verify_ssl = verify_ssl
        self._verify_method = verify_method
        self._verify_warnings = verify_warnings
        self._version = version
        self._dryrun = dryrun

        self.warnings = []

        if not self._verify_warnings:
            reason = (
                'Verifying TLS connection to %s disabled.' %
                self._host
            )
            self.warnings.append(reason)
            urllib3.disable_warnings()

        self._baseaddress = (
            "%s://%s:%s" %
            (
                self._protocol,
                self._host,
                self._port
            )
        )

        self._baseurl = (
            "%s/scalemgmt/%s" %
            (
                self._baseaddress,
                self._version
            )
        )

        self._session = requests.Session()
        self._session.url = self._baseurl
        self._session.verify = self._verify_ssl

        self._session.headers.update(
            {'accept': 'application/json'}
        )
        self._session.headers.update(
            {'content-type': 'application/json'}
        )
        self._session.auth = requests.auth.HTTPBasicAuth(
            self._username,
            self._password
        )

    def _get(
        self,
        commandurl: type=str,
        params: Union[None, dict]=None
    ):
        """
        @brief This exposes a raw get method for the session
        """
        response = self._session.get(
            url=commandurl,
            params=params
        )

        # Do something about paged responses here
        while 'paging' in response.json():
            commandurl = (
                self._baseaddress +
                response.json()['paging']['baseUrl']
            )

            params = {
                'lastId': response.json()['paging']['lastId']
            }

            if 'fields' in response.json()['paging']:
                params['fields'] = response.json()['paging']['fields']

            nextresponse = self._get(
                commandurl=commandurl,
                params=params
            )

            mockjson = {}
            for key in nextresponse.json():
                if key in ['paging', 'status']:
                    mockjson[key] = nextresponse.json()[key]
                else:
                    if key in response.json():
                        mockjson[key] = nextresponse.json()[key] + response.json()[key]
                    else:
                        mockjson[key] = nextresponse.json()[key]

            response = nextresponse
            response._content = bytes(json.dumps(mockjson, indent=2, sort_keys=True), encoding='utf-8')

        return response

    def _post(
        self,
        commandurl: type=str,
        data: type=dict
    ):
        """
        @brief This exposes a raw post method for the internal session
        """
        return self._session.post(
            url=commandurl,
            data=json.dumps(data)
        )

    def _put(
        self,
        commandurl: type=str,
        data: type=dict
    ):
        """
        @brief This exposes a raw put method for the internal session
        """
        return self._session.put(
            url=commandurl,
            data=json.dumps(data)
        )

    def _prepget(
        self,
        commandurl: type=str,
        data: type=dict
    ):
        """
        @brief This cleans up the args and parameters posts the and creates a prepared GET reques from the internal sessions object

        @param self This object
        @param commandurl the URL for the request
        @param data a dictionary of arguments and parameters

        @return a requests.Response object
        """

        request = requests.Request(
            'GET',
            url=commandurl,
            data=json.dumps(data)
        )

        return self._session.prepare_request(request)

    def _preppost(
        self,
        commandurl: type=str,
        data: type=dict
    ):
        """
        @brief This cleans up the args and parameters posts the and creates a prepared PUSH reques from the internal sessions object

        @param self This object
        @param commandurl the URL for the request
        @param data a dictionary of arguments and parameters

        @return a requests.Response object
        """

        request = requests.Request(
            'POST',
            url=commandurl,
            data=json.dumps(data)
        )

        return self._session.prepare_request(request)

    def _prepput(
            self,
            commandurl: type=str,
            data: type=dict
    ):
        """
        @brief This cleans up the args and parameters posts the and creates a prepared PUT reques from the internal sessions object

        @param self This object
        @param commandurl the URL for the request
        @param data a dictionary of arguments and parameters

        @return a requests.Response object
        """

        request = requests.Request(
            'PUT',
            url=commandurl,
            data=json.dumps(data)
        )

        return self._session.prepare_request(request)

    def clearwarnings(self):
        """
        @brief      Retrieve and clear the warning array

        @param      self  The object

        @return     the warnings array before it was cleared
        """
        warnings = self.warnings
        self.warnings = []
        return warnings

    def info(self):
        """
        @brief      Returns the response from the info command

        @param      self  The object

        @return     the requests.Response from the info request
        """
        commandurl = "%s/info" % self._baseurl
        return self._get(commandurl)

    def config(self):
        """
        @brief      { function_description }

        @param      self    The object
        @param      job_id  The job identifier

        @return     { description_of_the_return_value }
        """
        commandurl = "%sconfig" % self._baseurl
        return self._get(commandurl)

## WRITE METHODS: Methods beyond this point can update spectrumscale
## these methods MUST make no changes if self._dryrun is True
##

    def send(
        self,
        preprequest: type=requests.PreparedRequest
    ):
        response = None
        if self._dryrun:
            response = jsonprepreq(preprequest)
            response['dryrun'] = True
        else:
            response = self._session.send(preprequest)

        return response
