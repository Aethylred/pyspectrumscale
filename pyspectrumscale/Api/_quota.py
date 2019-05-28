"""
Methods for pyspectrumscale.Api that deal with quotas
"""
from typing import Union


def get_quota(
        self,
        filesystem: str,
        fileset: Union[str, None]=None,
        filter: Union[None, str]=None,
        allfields: bool=False
):
    """
    @brief      List all quotas or return a specific quota for a fileset

    @param      self        The object
    @param      filesystem  The filesystem name
    @param      fileset The fileset to get quotas from, if none gets all quotas from the filesystem

    @return     The request response as a Response.requests object
    """
    params = {}
    if allfields is not None:
        params['fields'] = ':all:'
    if filter is not None:
            params['filter'] = filter

    if fileset is not None:
        commandurl = "%s/filesystems/%s/filesets/%s/quotas" % (
            self._baseurl,
            filesystem,
            fileset
        )
    else:
        commandurl = "%s/filesystems/%s/quotas" % (
            self._baseurl,
            filesystem
        )

    return self._get(
        commandurl,
        params=params
    )


def quota(
        self,
        filesystem: str,
        fileset: Union[str, None]=None,
        filter: Union[None, str]=None,
        allfields: bool=False
):
    """
    @brief      List all quotas or return a specific quota for a fileset

    @param      self        The object
    @param      filesystem  The filesystem name
    @param      fileset The fileset to get quotas from, if none gets all quotas from the filesystem

    @return     The request response as a Response.requests object
    """

    response = None
    quotaresponse = self.get_quota(
        filesystem=filesystem,
        fileset=fileset,
        filter=filter,
        allfields=allfields
    )

    if quotaresponse.ok:
        response = quotaresponse.json()['quotas']
        if len(response) == 1:
            response = response[0]

    return response

def quotas(
        self,
        filesystems: Union[str, list, None]=None,
        filesets: Union[str, list, None]=None,
        filter: Union[None, str]=None,
        allfields: Union[bool, None]=None
):
    """
    @brief      This method returns the list of matching quotas as JSON with the response stripped away.

    @param      self        The object
    @param      filesystems  The filesystem
    @param      fileset     The fileset

    @return     { description_of_the_return_value }
    """

    response = []

    if filesystems is None:
        response = self.quotas(
            filesystems=self.list_filesystems(),
            filesets=filesets,
            filter=filter,
            allfields=allfields
        )
    elif isinstance(filesystems, list):
        for fs in filesystems:
            fsresponse = self.quotas(
                filesystems=fs,
                filesets=filesets,
                filter=filter,
                allfields=allfields
            )
            if isinstance(fsresponse, list):
                response += fsresponse
            else:
                if fsresponse is not None:
                    response.append(fsresponse)
    else:
        if isinstance(filesets, list):
            for fs in filesets:
                fsresponse = self.quota(
                    filesystem=filesystems,
                    fileset=fs,
                    filter=filter,
                    allfields=allfields
                )
                if isinstance(fsresponse, list):
                    response += fsresponse
                else:
                    if fsresponse is not None:
                        response.append(fsresponse)
        else:
            fsresponse = self.quota(
                filesystem=filesystems,
                fileset=filesets,
                filter=filter,
                allfields=allfields
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

## WARNING: The following methods can wite to the Spectrum Scale filsystem
## These methods must make no changes if dryrun is true
##

def preppost_quota(
    self,
    filesystem: type=str,
    fileset: type=str,
    blocksoftlimit: Union[None, str]=None,
    blockhardlimit: Union[None, str]=None,
    blockgraceperiod: Union[None, str]=None,
    filessoftlimit: Union[None, str]=None,
    fileshardlimit: Union[None, str]=None,
    filesgraceperiod: Union[None, str]=None,
    quotatype: Union[None, str]="FILESET"
):
    print('do something')
