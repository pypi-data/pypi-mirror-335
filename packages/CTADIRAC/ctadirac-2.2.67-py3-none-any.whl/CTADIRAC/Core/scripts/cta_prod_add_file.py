#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
import os
from multiprocessing import Pool

# DIRAC imports
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.Core.Security.ProxyInfo import getProxyInfo
from DIRAC.DataManagementSystem.Client.DataManager import DataManager

from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file

Script.setUsageMessage(
    """
Bulk upload of a list of local files from the current directory to a Storage Element
Usage:
   cta-prod-add-file <ascii file with lfn list> <SE>
"""
)

Script.parseCommandLine(ignoreErrors=True)

args = Script.getPositionalArgs()
if len(args) > 1:
    infile = args[0]
    SE = args[1]
else:
    Script.showHelp()

DIRAC.initialize()

res = getProxyInfo()

if not res["OK"]:
    gLogger.error("Error getting proxy info")
    DIRAC.exit(2)

voName = res["Value"]["VOMS"][0].split("/")[1]


@Script()
def main():
    infileList = read_inputs_from_file(infile)
    p = Pool(10)
    p.map(addfile, infileList)


def addfile(lfn):
    start_path = lfn.split("/")[1]
    if start_path != voName:
        gLogger.error(f"Wrong lfn: path must start with vo name {voName}:\n {lfn}")
        return
    dm = DataManager(vo=voName)
    res = dm.putAndRegister(lfn, os.path.basename(lfn), SE)
    if not res["OK"]:
        gLogger.error("Error uploading file", lfn)
        return res["Message"]


if __name__ == "__main__":
    main()
