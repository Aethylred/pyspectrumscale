"""
pyspectrumscale.api methods for filesystems
"""
from typing import Union


def get_filesystem(
        self,
        filesystem: Union[str, None]=None
):
    """
    @brief      List all filesystems or return a specific filesystem

    @param      self        The object
    @param      filesystem  The filesystem name, default None, which returns all filesystems

    @return     The request response as a Response.requests object
    """
    if filesystem:
        commandurl = "%s/filesystems/%s" % (
            self._baseurl,
            filesystem
        )
    else:
        commandurl = "%s/filesystems" % self._baseurl

    return self._get(commandurl)


def list_filesystems(
        self,
        filesystems: Union[str, list, None]=None
):
    """
    @brief      List all filesystems or return a specific filesystem

    @param      self        The object
    @param      filesystem  The filesystem name, default None, which returns all filesystems

    @return     Just the JSON content from the response
    """

    fslist = []

    if isinstance(filesystems, list):
        for fs in filesystems:
            if fs:
                fslist += self.filesystems(fs)
    else:
        fsresponse = self.get_filesystem(filesystem=filesystems)
        if fsresponse.ok:
            for fs in fsresponse.json()['filesystems']:
                fslist.append(fs['name'])

    return fslist


def filesystem(
        self,
        filesystem: str
):
    """
    @brief      List a specific filesystem as a JSON dict

    @param      self        The object
    @param      filesystem  The filesystem name

    @return     Just the JSON content from the response as a dict
    """

    fs = None
    fsresponse = self.get_filesystem(filesystem=filesystem)
    if fsresponse.ok:
        fs = fsresponse.json()['filesystems'][0]

    return fs


def filesystems(
        self,
        filesystems: Union[str, list, None]=None
):
    """
    @brief      List all filesystems or return a specific filesystem as a dict

    @param      self        The object
    @param      filesystem  The filesystem name, or list of names, default None, which returns all filesystems

    @return     Just the JSON content from the response as a dict
    """

    fslist = []
    if filesystems is None:
        fslist = self.filesystems(self.list_filesystems())
    elif isinstance(filesystems, list):
        for fs in filesystems:
            if fs:
                fslist.append(self.filesystem(fs))
    else:
        fslist.append(self.filesystem(filesystems))

    return fslist
