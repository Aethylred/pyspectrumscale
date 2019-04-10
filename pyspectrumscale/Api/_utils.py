"""
Miscellaneous utilities for pyspectrumscale.API
"""
import pathlib
import urllib


# This converts a file path into something safe
# to send as a REST URI
def truncsafepath(
    path: type=str
):
    pathtail = pathlib.Path(path).parts[2:]
    mountpath = str(pathlib.PurePath(*pathtail).as_posix())
    return urllib.parse.quote(mountpath, safe='')
