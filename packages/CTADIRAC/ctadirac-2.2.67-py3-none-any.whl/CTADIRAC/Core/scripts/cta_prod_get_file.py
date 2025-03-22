#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
import os
import signal
from multiprocessing import Pool

# DIRAC imports
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.DataManagementSystem.Client.DataManager import DataManager

from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file

Script.setUsageMessage(
    """
Download files from a list of lfns with N parallel process
Usage:
   cta-prod-get-file [options] <ascii file with lfn list> --NbProcess=8

For less verbose output use option:
   cta-prod-get-file -o LogLevel=NOTICE
"""
)

Script.registerSwitch("", "NbProcess=", "    number of process")
switches, args = Script.parseCommandLine(ignoreErrors=True)

DIRAC.initialize()

TEMPDIR = ".incomplete"


def sigint_handler(signum, frame):
    """
    Raise KeyboardInterrupt on SIGINT (CTRL + C)
    This should be the default, but apparently Dirac changes it.
    """
    raise KeyboardInterrupt()


def getfile(lfn):
    voName = lfn.split("/")[1]
    if voName not in ["ctao", "vo.cta.in2p3.fr"]:
        message = (
            f"Wrong lfn: path must start with vo name (ctao or vo.cta.in2p3.fr):\n{lfn}"
        )
        gLogger.error(message)
        return
    dm = DataManager(vo=voName)
    res = dm.getFile(lfn)
    if not res["OK"]:
        gLogger.error("Error downloading file", lfn)
        return res["Message"]

    name = os.path.basename(lfn)
    os.rename(os.path.join(".incomplete", name), name)
    gLogger.notice("Successfully downloaded file", lfn)


@Script()
def main():
    if len(args) == 1:
        infile = args[0]
    else:
        Script.showHelp()

    nbProcess = 8
    for switch in switches:
        if switch[0] == "NbProcess":
            nbProcess = int(switch[1])

    # put files currently downloading in a subdirectory
    # to know which files have already finished
    if not os.path.exists(TEMPDIR):
        os.makedirs(TEMPDIR)

    infileList = read_inputs_from_file(infile)
    # see https://stackoverflow.com/a/35134329/3838691
    # ignore sigint before creating the pool,
    # so child processes inherit the setting, we will terminate them
    # if the master process catches sigint
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    p = Pool(nbProcess)
    # add the original handler back
    signal.signal(signal.SIGINT, sigint_handler)

    try:
        future = p.map_async(getfile, infileList)

        while not future.ready():
            future.wait(5)
    except (SystemExit, KeyboardInterrupt):
        gLogger.fatal("Received SIGINT, waiting for subprocesses to terminate")
        p.close()
        p.terminate()
    finally:
        p.close()
        p.join()
        if len(os.listdir(TEMPDIR)) == 0:
            os.rmdir(TEMPDIR)


if __name__ == "__main__":
    main()
