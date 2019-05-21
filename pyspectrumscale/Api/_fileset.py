"""
Methods for pyspectrumscale.Api that deal with filesets
"""
from typing import Union
import json


def get_fileset(
        self,
        filesystem: Union[str, None],
        fileset: Union[str, None]=None,
        allfields: Union[bool, None]=None
):
    """
    @brief      List all filesystems or return a specific filesystem

    @param      self        The object
    @param      filesystem  The filesystem name, default None, which returns all filesystems

    @return     The request response as a Response.requests object
    """

    params = {}
    if allfields is not None:
        params['fields'] = ':all:'

    if fileset is not None:
        commandurl = "%s/filesystems/%s/filesets/%s" % (
            self._baseurl,
            filesystem,
            fileset
        )
    else:
        commandurl = "%s/filesystems/%s/filesets" % (
            self._baseurl,
            filesystem
        )

    return self._get(
        commandurl,
        params=params
    )


def fileset(
        self,
        filesystem: str,
        fileset: Union[str, None]=None,
        allfields: Union[bool, None]=None
):
    """
    @brief      This method returns a specifc fileset from a specific filesystem as JSON with the response stripped away.

    @param      self        The object
    @param      filesystem  The filesystem
    @param      fileset     The fileset

    @return     { description_of_the_return_value }
    """

    response = None
    fsresponse = self.get_fileset(
        filesystem=filesystem,
        fileset=fileset,
        allfields=allfields
    )

    if fsresponse.ok:
        if len(fsresponse.json()['filesets']) == 1:
            response = fsresponse.json()['filesets'][0]
        else:
            response = fsresponse.json()['filesets']

    return response


def filesets(
        self,
        filesystems: Union[str, list, None]=None,
        filesets: Union[str, list, None]=None,
        allfields: Union[bool, None]=None
):
    """
    @brief      This method returns the list of matching filesets as JSON with the response stripped away.

    @param      self        The object
    @param      filesystems  The filesystem
    @param      fileset     The fileset

    @return     { description_of_the_return_value }
    """

    response = []

    if filesystems is None:
        response = self.filesets(
            filesystems=self.get_filesystem(),
            filesets=filesets,
            allfields=allfields
        )
    elif isinstance(filesystems, list):
        for fs in filesystems:
            fsresponse = self.filesets(
                filesystems=fs,
                filesets=filesets,
                allfields=allfields
            )
            if isinstance(fsresponse, list):
                response += fsresponse
            else:
                response.append(fsresponse)
    else:
        if isinstance(filesets, list):
            for fs in filesets:
                fsresponse = self.fileset(
                    filesystem=filesystems,
                    fileset=filesets,
                    allfields=allfields
                )
                if isinstance(fsresponse, list):
                    response += fsresponse
                else:
                    response.append(fsresponse)
        else:
            fsresponse = self.fileset(
                filesystem=filesystems,
                fileset=filesets,
                allfields=allfields
            )
            if isinstance(fsresponse, list):
                response += fsresponse
            else:
                response.append(fsresponse)

    if isinstance(response, list):
        if len(response) == 1:
            response = response[0]

    return response


def list_filesets(
        self,
        filesystem: Union[str, None],
        fileset: Union[str, None]=None
):
    """
    @brief      This methdo returns the list of matching filesets as JSON with the response stripped away.

    @param      self        The object
    @param      filesystem  The filesystem
    @param      fileset     The fileset

    @return     { description_of_the_return_value }
    """

    response = self.fileset(
        filesystem,
        fileset
    )

    filesets = []

    if isinstance(response, list):
        for fileset in response:
            filesets.append(fileset['filesetName'])
    else:
        filesets.append(response['filesetName'])

    return filesets
