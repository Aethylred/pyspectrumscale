"""
Methods for pyspectrumscale.Api that deal with access control lists (ACLs)

WARNING: There are no 'all acls' queries in the Spectrum Scale API
This means that all bulk operations require a query per path
to retrieve their acl (two queries for a fileset).

Requesting all acls from a filesystem or all filesystems can take many minutes
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
    acl = None
    response = None

    if fileset is not None:
        fs = self.fileset(
            filesystem=filesystem,
            fileset=fileset,
            allfields=True
        )
        if fs is not None:
            path = fs['config']['path']

    if path is not None:
        response = self.get_acl(
            filesystem=filesystem,
            path=path,
            allfields=allfields
        )
        if response is not None:
            if 'acl' in response.json():
                acl = response.json()['acl']
                # tag the acl with the path
                acl['path'] = path
    else:
        acl = []
        for fileset in self.list_filesets(
            filesystem=filesystem
        ):
            aclresponse = self.acl(
                filesystem=filesystem,
                fileset=fileset,
                allfields=allfields
            )
            if aclresponse is not None:
                acl.append(aclresponse)

    if isinstance(acl, list):
        if len(acl) == 1:
            acl = acl[0]

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
            paths=paths,
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
        # So do filesets first, then paths, but check we don't already have that acl
        if filesets is not None:
            if isinstance(filesets, list):
                for fs in filesets:
                    fsresponse = self.acl(
                        filesystem=filesystems,
                        fileset=fs,
                        allfields=allfields
                    )
                    if isinstance(fsresponse, list):
                        for acl in fsresponse:
                            matches = next(
                                (item for item in acls if item['path'] == acl['path']),
                                None
                            )
                            if matches is None:
                                acls.append(acl)
                    else:
                        if fsresponse is not None:
                            matches = next(
                                (item for item in acls if item['path'] == fsresponse['path']),
                                None
                            )
                            if matches is None:
                                acls.append(fsresponse)
            else:
                fsresponse = self.acl(
                    filesystem=filesystems,
                    fileset=filesets,
                    allfields=allfields
                )
                if isinstance(fsresponse, list):
                    for acl in fsresponse:
                        matches = next(
                            (item for item in acls if item['path'] == acl['path']),
                            None
                        )
                        if matches is None:
                            acls.append(acl)
                else:
                    if fsresponse is not None:
                        matches = next(
                            (item for item in acls if item['path'] == fsresponse['path']),
                            None
                        )
                        if matches is None:
                            acls.append(fsresponse)
        if paths is not None:
            if isinstance(paths, list):
                for path in filesets:
                    pathresponse = self.acl(
                        filesystem=filesystems,
                        path=path,
                        allfields=allfields
                    )
                    if isinstance(pathresponse, list):
                        for acl in pathresponse:
                            matches = next(
                                (item for item in acls if item['path'] == acl['path']),
                                None
                            )
                            if matches is None:
                                acls.append(acl)
                    else:
                        if pathresponse is not None:
                            matches = next(
                                (item for item in acls if item['path'] == pathresponse['path']),
                                None
                            )
                            if matches is None:
                                acls.append(pathresponse)
            else:
                pathresponse = self.acl(
                    filesystem=filesystems,
                    path=paths,
                    allfields=allfields
                )
                if isinstance(pathresponse, list):
                    for acl in pathresponse:
                        matches = next(
                            (item for item in acls if item['path'] == acl['path']),
                            None
                        )
                        if matches is None:
                            acls.append(acl)
                else:
                    if pathresponse is not None:
                        matches = next(
                            (item for item in acls if item['path'] == pathresponse['path']),
                            None
                        )
                        if matches is None:
                            acls.append(pathresponse)

        if not paths and not filesets:
            fsresponse = self.acls(
                filesystems=filesystems,
                filesets=self.list_filesets(filesystems),
                allfields=allfields
            )
            if isinstance(fsresponse, list):
                for acl in fsresponse:
                    matches = next(
                        (item for item in acls if item['path'] == acl['path']),
                        None
                    )
                    if matches is None:
                        acls.append(acl)
            else:
                if fsresponse is not None:
                    matches = next(
                        (item for item in acls if item['path'] == fsresponse['path']),
                        None
                    )
                    if matches is None:
                        acls.append(fsresponse)


    if not acls:
        acls = None
    if isinstance(acls, list):
        if len(acls) == 1:
            acls = acls[0]

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
        filesystem=filesystem,
        allfields=True
    )

    acls = {}

    if isinstance(filesets, list):
        for fileset in filesets:
            summary = {
                'path': fileset['config']['path']
            }
            summary['acl'] = self.acl(
                filesystem=filesystem,
                path=fileset['config']['path'],
                allfields=True
            )
            acls[fileset['filesetName']] = summary
    elif filesets is not None:
        summary = {
            'path': filesets['config']['path']
        }
        summary['acl'] = self.acl(
            filesystem=filesystem,
            path=filesets['config']['path'],
            allfields=True
        )
        acls[filesets['filesetName']] = summary

    return acls

