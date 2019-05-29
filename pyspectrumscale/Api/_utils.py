"""
Miscellaneous utilities for pyspectrumscale.API
"""
import pathlib
import urllib
import requests
import json
import re
import sys
from quantities import kibi, mebi, gibi, tebi, pebi


# This converts a file path into something safe
# to send as a REST URI
def truncsafepath(
    path: type=str
):
    """
    """

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


def validinodestr(
        inodestr: str
):
    """
    @brief      Checks that an Scale quota inode string is valid
    """

    inode_validator = re.compile("^\d+\.?\d*[KGM]?$")
    return inode_validator.match(str(inodestr))


def validblockstr(
        blockstr: str
):
    """
    @brief      Checks that an Scale quota block string is valid
    """
    block_validator = re.compile("^\d+\.?\d*[KGMTP]?$")
    return block_validator.match(str(blockstr))


def validgracestr(
        gracestr: str
):
    """
    @brief      Checks that an Scale grace time period string is valid
    """
    grace_validator = re.compile("^\d+\.?\d*(seconds|minutes|hours|days)$")
    return grace_validator.match(str(gracestr))


def blocktoint(
        blockstr: str
):
    """
    @brief      This function turns a block size string enting with K,M,G,T,P into a Kibi, Mibi, Gibi, Tibi, or Pibi int value respectivly.

    @param      blockstr  The blockstr

    @return     the int value of the blockstr
    """

    result = None

    # is block string valid
    if validblockstr(blockstr):
        # is it just a digit
        if isinstance(blockstr, int):
            result = blockstr
        elif blockstr.isdigit():
            result = int(blockstr)
        elif blockstr[-1] in ['K', 'M', 'G', 'T']:
            # Process
            if blockstr[-1] == 'K':
                result = int(float(blockstr[:-1]) * kibi)
            elif blockstr[-1] == 'M':
                result = int(float(blockstr[:-1]) * mebi)
            elif blockstr[-1] == 'G':
                result = int(float(blockstr[:-1]) * gibi)
            elif blockstr[-1] == 'T':
                result = int(float(blockstr[:-1]) * tebi)
            elif blockstr[-1] == 'P':
                result = int(float(blockstr[:-1]) * pebi)
    else:
        print(
            "ERROR: %s is not a valid block string for spectrumscale" %
            blockstr,
            file=sys.stderr
        )

    return result


def inodetoint(
        inodestr: str
):
    """
    @brief      This function turns a inode size string enting with K,M,G into a Kibi, Mibi, or Gibi int value respectivly.

    @param      blockstr  The blockstr

    @return     the int value of the blockstr
    """
    result = None

    # is block string valid
    if validinodestr(inodestr):
        # is it just a digit
        if isinstance(inodestr, int):
            result = inodestr
        elif inodestr.isdigit():
            result = int(inodestr)
        elif inodestr[-1] in ['K', 'M', 'G']:
            # Process
            if inodestr[-1] == 'K':
                result = int(float(inodestr[:-1]) * kibi)
            elif inodestr[-1] == 'M':
                result = int(float(inodestr[:-1]) * mebi)
            elif inodestr[-1] == 'G':
                result = int(float(inodestr[:-1]) * gibi)
    else:
        print(
            "ERROR: %s is not a valid file/inode string for spectrumscale" %
            inodestr,
            file=sys.stderr
        )

    return result


def blockcompare(
        block1: str,
        block2: str
):
    """
    @brief      Compare two Scale block strings

    @param      block1  The block 1
    @param      block2  The block 2

    @return     { description_of_the_return_value }
    """
    result = None
    # Check if block1 and block 2 are valid
    blkint1 = blocktoint(block1)
    blkint2 = blocktoint(block2)

    # if the blocks are invalid return none
    if blkint1 is None or blkint2 is None:
        return None

    # Compare block1 and block2
    result = blkint1 - blkint2

    return int(result)


def inodecompare(
        inode1: str,
        inode2: str
):
    """
    @brief      Compares two Scale inode strings

    @param      inode1  The inode 1
    @param      inode2  The inode 2

    @return     { description_of_the_return_value }
    """
    result = None
    # Check if inode1 and inode 2 are valid
    inodeint1 = inodetoint(inode1)
    inodeint2 = inodetoint(inode2)

    # if the blocks are invalid return none
    if inodeint1 is None or inodeint2 is None:
        return None

    # Compare block1 and block2
    result = inodeint1 - inodeint2

    return int(result)
