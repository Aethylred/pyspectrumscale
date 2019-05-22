"""
Methods for pyspectrumscale.Api that deal with access control lists (ACLs)
"""
import sys
from typing import Union
from ._utils import truncsafepath


def get_acl(
        self,
        filesystem: Union[str, None],
        path: Union[str, None],
        allfields: bool=False
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

    commandurl = "%s/filesystems/%s/acl/%s" % (
        self._baseurl,
        filesystem,
        truncsafepath(path)
    )

    return self._get(
        commandurl,
        params=params
    )


def acl(
        self,
        filesystem: Union[str, None],
        path: Union[str, None]=None,
        fileset: Union[str, None]=None,
        allfields: bool=False
):
    """
    @brief      { function_description }

    @param      self        The object
    @param      filesystem  The filesystem
    @param      path        The path

    @return     { description_of_the_return_value }
    """

    if fileset is not None:
        path = self.fileset(
            filesystem=filesystem,
            fileset=fileset
        )['config']['path']

    response = self.get_acl(
        filesystem=filesystem,
        path=path,
        allfields=allfields
    )

    acl = None
    if 'acl' in response.json():
        acl = response.json()['acl']

    return acl


def acls(
        self,
        filesystems: Union[str, None]=None,
        filesets: Union[str, None]=None,
        paths: Union[str, None]=None,
        allfields: bool=False
):
    """
    @brief      { function_description }

    @param      self        The object
    @param      filesystem  The filesystem
    @param      path        The path

    @return     { description_of_the_return_value }
    """

    acls = []

    if filesystems is None:
        acls = self.acls(
            filesystems=self.list_filesystems(),
            filesets=filesets,
            paths=path,
            allfields=allfields
        )
    elif isinstance(filesystems, list):
        for fs in filesystems:
            aclresponse = self.acls(
                filesystems=fs,
                filesets=filesets,
                paths=paths,
                allfields=allfields
            )
            if isinstance(aclresponse, list):
                acls += aclresponse
            else:
                if aclresponse is not None:
                    acls.append(aclresponse)
    else:
        # The trick here is to parse paths and filesets without duplicating the acls

    if isinstance(acls, list):
        if len(acls) == 1:
            acls = acls[0]

    if not acls:
        acls = None

    return acls


def list_acls(
        self,
        filesystem: Union[str, None]
):
    """
    @brief      { function_description }

    @param      self        The object
    @param      filesystem  The filesystem

    @return     { description_of_the_return_value }
    """

    filesets = self.fileset(
        filesystem,
        allfields=True
    )

    acls = {}

    if isinstance(filesets, list):
        for fileset in filesets:
            summary = {
                'path': fileset['config']['path']
            }
            summary['acl'] = self.acl(
                filesystem,
                path=fileset['config']['path'],
                allfields=True
            )
            acls[fileset['filesetName']] = summary
    else:
        summary = {
            'path': filesets['config']['path']
        }
        summary['acl'] = self.acl(
            filesystem,
            path=filesets['config']['path'],
            allfields=True
        )
        acls[filesets['filesetName']] = summary

    return acls

