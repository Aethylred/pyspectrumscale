"""
pyspectrumscale.api methods for filesystems
"""
from typing import Union


def filesystem(
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

    print(commandurl)
    return self._get(commandurl)
