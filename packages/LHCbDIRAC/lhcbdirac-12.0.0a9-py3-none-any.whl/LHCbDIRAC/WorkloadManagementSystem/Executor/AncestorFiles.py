###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""The LHCb AncestorFiles executor queries the Bookkeeping catalogue for ancestor
files if the JDL parameter AncestorDepth is specified.

The ancestor files are subsequently added to the existing input data
requirement of the job.
"""

from DIRAC import S_OK, S_ERROR
from DIRAC.WorkloadManagementSystem.Executor.Base.OptimizerExecutor import OptimizerExecutor
from DIRAC.WorkloadManagementSystem.DB.JobDB import JobDB
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient


class AncestorFiles(OptimizerExecutor):
    """
    The specific Optimizer must provide the following methods:
      - initializeOptimizer() before each execution cycle
      - optimizeJob() - the main method called for each job
    """

    @classmethod
    def initializeOptimizer(cls):
        """Initialize specific parameters for AncestorFiles executor."""
        cls.bk = BookkeepingClient()
        cls.jobDB = JobDB()
        return S_OK()

    def optimizeJob(self, jid, jobState):
        """This method checks the input data with ancestors.

        The original job JDL is always extracted to obtain the input data,
        therefore rescheduled jobs will not recursively search for ancestors
        of ancestors etc.
        """
        inputData = []
        if jobState.lookupAttribute("InputData"):
            inputData = jobState.getListFromExpression("InputData")

        if not jobState.lookupAttribute("AncestorDepth"):
            self.log.warn(f"No AncestorDepth requirement found for job {jid}")
            return S_ERROR("AncestorDepth Not Found")

        ancestorDepth = jobState.getAttributeInt("AncestorDepth")

        if ancestorDepth == 0:
            return S_OK("Null AncestorDepth specified")

        self.log.info(
            f"Job {jid} has {len(inputData)} input data files and specified ancestor depth of {ancestorDepth}"
        )
        result = self.__getInputDataWithAncestors(jid, inputData, ancestorDepth)
        if not result["OK"]:
            return result

        newInputData = result["Value"]

        jobState.insertAttributeVectorString("InputData", newInputData)
        newJDL = jobState.asJDL()
        if not (result := self.__setJobInputData(jid, newJDL, newInputData))["OK"]:
            return result

        return self.setNextOptimizer()

    ############################################################################
    def __getInputDataWithAncestors(self, job, inputData, ancestorDepth):
        """Extend the list of LFNs with the LFNs for their ancestor files for the
        generation depth specified in the job JDL."""
        inputData = [i.replace("LFN:", "") for i in inputData]
        result = self.bk.getFileAncestors(inputData, ancestorDepth, replica=True)
        if not result["OK"]:
            self.log.warn(result["Message"])
            return result

        ancestors = [anc["FileName"] for ancList in result["Value"]["Successful"].values() for anc in ancList]

        return S_OK(ancestors + inputData)

    def __setJobInputData(self, job, jdl, inputData):
        """Sets the new job input data requirement including ancestor files."""
        inputData = [i.replace("LFN:", "") for i in inputData]

        if not (result := self.jobDB.setInputData(job, inputData))["OK"]:
            self.log.error(result["Message"])
            return result

        if not (result := self.jobDB.setJobJDL(job, jdl))["OK"]:
            self.log.error(result["Message"])
            return result

        return S_OK("Job updated")
