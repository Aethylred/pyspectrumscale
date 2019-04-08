"""
{ item_description }
"""
from typing import Union


def fileset(
        self,
        filesystem: Union[str, None],
        fileset: Union[str, None]=None
):
    """
    @brief      List all filesystems or return a specific filesystem

    @param      self        The object
    @param      filesystem  The filesystem name, default None, which returns all filesystems

    @return     The request response as a Response.requests object
    """

    if fileset:
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

    print(commandurl)
    return self._get(commandurl)
