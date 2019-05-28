"""
Miscellaneous utilities for pyspectrumscale.API
"""
import pathlib
import urllib
import requests
import json


# This converts a file path into something safe
# to send as a REST URI
def truncsafepath(
    path: type=str
):
    pathtail = pathlib.Path(path).parts[2:]
    mountpath = str(pathlib.PurePath(*pathtail).as_posix())
    return urllib.parse.quote(mountpath, safe='')


def jsonprepreq(
    preprequest: type=requests.PreparedRequest
):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared". but we need it as JSONable dict
    """
    jsonprepreq = {
        'headers': {},
        'body': {}
    }

    jsonprepreq['method'] = preprequest.method
    jsonprepreq['url'] = preprequest.url
    for key, value in preprequest.headers.items():
        jsonprepreq['headers'][key] = value

    jsonprepreq['body'] = json.loads(preprequest.body)
    return jsonprepreq
