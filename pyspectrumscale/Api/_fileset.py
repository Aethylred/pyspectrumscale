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
    @brief      List all filesets or return a specific fileset from a filesystem

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
        allfields: Union[bool, None]=None,
        acl: bool=False,
        quota: bool=False,
        owner: bool=False,
        everything: bool=False
):
    """
    @brief      This method returns a specifc fileset from a specific filesystem as JSON with the response stripped away.

    @param      self        The object
    @param      filesystem  The filesystem
    @param      fileset     The fileset

    @return     { description_of_the_return_value }
    """

    # everything overrides all the other arguments
    if everything:
        acl = True
        quota = True
        owner = True
        allfields = True

    response = None
    fsresponse = self.get_fileset(
        filesystem=filesystem,
        fileset=fileset,
        allfields=allfields
    )

    if fsresponse.ok:
        response = fsresponse.json()['filesets']

        if acl or quota or owner:
            updatedfs = []

            for fs in response:
                if acl:
                    fsacl = self.acl(
                        filesystem=fs['filesystemName'],
                        path=fs['config']['path'],
                        allfields=allfields
                    )
                    if fsacl:
                        fs['config']['acl'] = fsacl

                updatedfs.append(fs)

            response = updatedfs

        # If it's a single element list, just return the element
        if len(response) == 1:
            response = response[0]

    return response


def filesets(
        self,
        filesystems: Union[str, list, None]=None,
        filesets: Union[str, list, None]=None,
        allfields: Union[bool, None]=None,
        acl: bool=False,
        quota: bool=False,
        owner: bool=False,
        everything: bool=False
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
            filesystems=self.list_filesystems(),
            filesets=filesets,
            allfields=allfields
        )
    elif isinstance(filesystems, list):
        for fs in filesystems:
            fsresponse = self.filesets(
                filesystems=fs,
                filesets=filesets,
                allfields=allfields,
                acl=acl,
                owner=owner,
                quota=quota,
                everything=everything
            )
            if isinstance(fsresponse, list):
                response += fsresponse
            else:
                if fsresponse is not None:
                    response.append(fsresponse)
    else:
        if isinstance(filesets, list):
            for fs in filesets:
                fsresponse = self.fileset(
                    filesystem=filesystems,
                    fileset=fs,
                    allfields=allfields,
                    acl=acl,
                    owner=owner,
                    quota=quota,
                    everything=everything
                )
                if isinstance(fsresponse, list):
                    response += fsresponse
                else:
                    if fsresponse is not None:
                        response.append(fsresponse)
        else:
            fsresponse = self.fileset(
                filesystem=filesystems,
                fileset=filesets,
                allfields=allfields,
                acl=acl,
                owner=owner,
                quota=quota,
                everything=everything
            )
            if isinstance(fsresponse, list):
                response += fsresponse
            else:
                if fsresponse is not None:
                    response.append(fsresponse)

    if isinstance(response, list):
        if len(response) == 1:
            response = response[0]

    if not response:
        response = None

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

## WRITABLE METHODS
## The following methods can create changes in the Spectrum Scale Filesystem
## Make sure that in all cases that they respect the dry-run flag

# Create a prepared request to create a fileset


def preppost_fileset(
    self,
    filesystem: type=str,
    fileset: type=str,
    path: type=str,
    owner: type=str,
    group: type=str,
    permissions: type=str,
    permissionchangemode: str='chmodAndUpdateAcl',
    parent: type=str,
    comment: type=str
):
    """
    @brief      Creates a pepared request to POST creation of a fileset. While this
                is not a writable method in itself, if it is sent to the self._session
                it will be executed. Using the self.send() method is recommended

    @param      self                  The object
    @param      filesystem            The filesystem
    @param      fileset               The fileset
    @param      path                  The path
    @param      owner                 The owner
    @param      group                 The group
    @param      permissions           The permissions
    @param      permissionchangemode  The permissionchangemode
    @param      parent                The parent
    @param      comment               The comment

    @return     a requests.PreparedRequest object
    """
    prepresponse = None

    commandurl = (
        "%s/filesystems/%s/filesets" % (
            self._baseurl,
            filesystem
        )
    )

    data = {
        'filesetName':  fileset,
        'path':         path,
        'owner':        ("%s:%s" % (owner, group)),
        'permissions':  permissions,
        'permissionChangeMode': permissionchangemode,
        'inodeSpace':   parent,
        'comment':      comment
    }

    prepresponse = self._preppost(
        commandurl=commandurl,
        data=data
    )

    return prepresponse
