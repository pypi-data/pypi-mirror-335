"""
OpenTMI Testcase module
"""
# Internal imports
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules
from opentmi_client.api.testcase.OtherInfo import OtherInfo
from opentmi_client.api.testcase.Execution import Execution
from opentmi_client.api.testcase.Status import Status
from opentmi_client.api.testcase.Compatible import Compatible


class Testcase(BaseApi):
    """
    Testcase class
    """
    def __init__(self, tcid):
        """
        Constructor for Testcase
        :param tcid: String
        """
        super().__init__()
        self.tcid = tcid
        self.status = Status()
        self.execution = Execution()
        self.other_info = OtherInfo()
        self.compatible = Compatible()

    def __str__(self):
        """
        Stringify function
        :return: String
        """
        return "{}".format(self.get("tcid", "?"))

    @property
    def tcid(self):
        """
        Getter for test case ID
        :return: String
        """
        return self.get("tcid")

    @tcid.setter
    @setter_rules()
    def tcid(self, value: str):
        """
        Setter for test case ID
        :param value: String
        """
        self.set("tcid", value)

    @property
    def other_info(self):
        """
        Getter for execution
        :return: OtherInfo
        """
        return self.get("other_info")

    @other_info.setter
    @setter_rules(OtherInfo)
    def other_info(self, value: OtherInfo):
        """
        Setter for other_info
        :param value: OtherInfo
        """
        self.set("other_info", value)

    @property
    def execution(self):
        """
        Getter for execution
        :return: String
        """
        return self.get("execution")

    @execution.setter
    @setter_rules(Execution)
    def execution(self, value: Execution):
        """
        Setter for execution
        :param value: String
        """
        self.set("execution", value)

    @property
    def status(self):
        """
        Getter for status
        :return: Status
        """
        return self.get("status")

    @status.setter
    @setter_rules(Status)
    def status(self, value: Status):
        """
        Setter for status
        :param value: Status
        """
        self.set("status", value)

    @property
    def compatible(self):
        """
        Getter for compatible
        :return: Compatible
        """
        return self.get("compatible")

    @compatible.setter
    @setter_rules(Compatible)
    def compatible(self, value: Compatible):
        """
        Setter for compatible
        :param value: Compatible
        """
        self.set("compatible", value)
