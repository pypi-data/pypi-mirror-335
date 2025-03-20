# Job.py

from DIRAC.Interfaces.API.Job import Job

class CTAOJob(Job):
    """Base Job class for CTAO jobs"""

    def __init__(self) -> None:
        Job.__init__(self)
        self.setName("ctaojob")
        #self.group="ctao"
        #self.VirtualOrganization="ctao"
        #self._addParameter(self.workflow, "VirtualOrganization", "JDL", "ctao", "VirtualOrganization")
