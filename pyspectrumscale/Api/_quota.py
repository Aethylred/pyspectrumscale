"""
Methods for pyspectrumscale.Api that deal with quotas
"""
import sys
from typing import Union
from ._utils import blocktoint, inodetoint, validgracestr


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
    """
    @brief      Creates a requests.PreparedRequest object to create a quota.
                This method makes NO CHECKS if the new quota is a good idea or not.
                The processes that call this method should check if the new quota
                would make the fileset/group/user unusable due to violating the
                new quota (i.e. check if usage > new quota)
                i.e. this methods assumes you know what you're doing

    @param      self              The object
    @param      filesystem        The filesystem
    @param      fileset           The fileset
    @param      blocksoftlimit    The blocksoftlimit
    @param      blockhardlimit    The blockhardlimit
    @param      blockgraceperiod  The blockgraceperiod
    @param      filessoftlimit    The filessoftlimit
    @param      fileshardlimit    The fileshardlimit
    @param      filesgraceperiod  The filesgraceperiod
    @param      quotatype         The quotatype

    @return     { description_of_the_return_value }
    """

    # Convert parameters to int
    blocksoftint = blocktoint(blocksoftlimit)
    blockhardint = blocktoint(blockhardlimit)
    filessoftint = inodetoint(filessoftlimit)
    fileshardint = inodetoint(fileshardlimit)

    validquota = True
    reasons = []
    prepresponse = None

    # Is soft block quota < hard block quota
    # and they both aren't 0
    if blocksoftlimit is not None and blockhardlimit is not None:
        if blocksoftint != 0 and blockhardint != 0:
            if blocksoftint >= blockhardint:
                reason = (
                    "Soft block limit (%s) is not"
                    " less than block hard limit (%s)" %
                    (
                        blocksoftlimit,
                        blockhardlimit
                    )
                )
                validquota = False
                reasons.append(reason)

    # Is soft block quota < hard block quota
    # and they both aren't 0
    if filessoftlimit is not None and fileshardlimit is not None:
        if filessoftint != 0 and fileshardint != 0:
            if filessoftint >= fileshardint:
                reason = (
                    "Soft inode limit (%s) is not"
                    " less than inode hard limit (%s)" %
                    (
                        filessoftlimit,
                        fileshardlimit
                    )
                )
                validquota = False
                reasons.append(reason)

    if validquota:
        if fileset is not None:
            commandurl = (
                "%sfilesystems/%s/quotas" % (
                    self._base_url,
                    filesystem
                )
            )
        else:
            commandurl = (
                "%sfilesystems/%s/filesets/%s/quotas" % (
                    self._base_url,
                    filesystem,
                    fileset
                )
            )

        data = {
            'operationType': 'setQuota',
            'quotaType': quotatype,
        }

        if fileset is not None:
            data['objectName'] = fileset

        if blocksoftlimit is not None:
            data['blockSoftLimit'] = blocksoftint

        if blockhardlimit is not None:
            data['blockHardLimit'] = blockhardint

        if filessoftlimit is not None:
            data['filesSoftLimit'] = filessoftint

        if fileshardlimit is not None:
            data['filesHardLimit'] = fileshardint

        if filesgraceperiod is not None:
            if validgracestr(filesgraceperiod):
                data['filesGracePeriod'] = filesgraceperiod

        if blockgraceperiod is not None:
            if validgracestr(blockgraceperiod):
                data['blockGracePeriod'] = blockgraceperiod

        prepresponse = self._preppost(
            commandurl=commandurl,
            data=data
        )

    else:
        for reason in reasons:
            print(
                ("ERROR: %s" % reason),
                file=sys.stderr
            )

    return prepresponse
