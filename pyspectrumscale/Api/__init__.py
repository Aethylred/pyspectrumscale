"""
Create an Api object that can communicate with the
Spectrum Scale Management API
"""
import json
from typing import Union
import requests
import urllib3

class Api:
    """
    @brief     Class to connect to the Spectrum Scale Management API
    """

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

        self._baseurl = (
            "%s://%s:%s/scalemgmt/%s" %
            (
                self._protocol,
                self._host,
                self._port,
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
            *dargs,
            **kwargs
    ):
        """
        @brief This exposes a raw get method for the session
        """
        response = self._session.get(
            *dargs,
            **kwargs
        )
        return response

    def _post(
            self,
            *dargs,
            **kwargs
    ):
        """
        @brief This exposes a raw post method for the internal session
        """
        response = self._session.post(
            *dargs,
            **kwargs
        )
        return response

    def _put(
            self,
            *dargs,
            **kwargs
    ):
        """
        @brief This exposes a raw put method for the internal session
        """
        response = self._session.put(
            *dargs,
            **kwargs
        )
        return response

    def get(
            self,
            method: str,
            args=None,
            params=None
    ):
        """
        @brief This cleans up the args and parameters posts the and handles
        the request and returns the response

        @param self This object
        @param method The Spectrum Scale Management API method to request
        @param args A list of arguments to be passed to the method request
        @param params A dictionary of parameters to be passed to the method request

        @return a requests.Response object
        """
        if args:
            if not isinstance(args, list):
                args = [args]
        else:
            args = []

        if not params:
            params = {}

        if self._version:
            params.setdefault('version', self._version)

        data = {
            'id': 0,
            'method': method,
            'params': [args, params]
        }

        response = self._get(
            self._session.url,
            data=json.dumps(data)
        )

        return response

    def prepget(
            self,
            method: str,
            args=None,
            params=None
    ):
        """
        @brief This cleans up the args and parameters posts the and creates a prepared GET reques from the internal sessions object

        @param self This object
        @param method The Spectrum Scale Management API method to request
        @param args A list of arguments to be passed to the method request
        @param params A dictionary of parameters to be passed to the method request

        @return a requests.Response object
        """
        if args:
            if not isinstance(args, list):
                args = [args]
        else:
            args = []

        if not params:
            params = {}

        data = {
            'id': 0,
            'method': method,
            'params': [args, params]
        }

        request = requests.Request(
            'GET',
            self._session.url,
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
        return self.get('info')
