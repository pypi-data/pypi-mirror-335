""" OpenTMI module """
# Internal imports
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules
from opentmi_client.api.testcase.Verification import Verification


class Status(BaseApi):
    """ Status class """
    def __init__(self):
        """ Constructor for Status """
        super().__init__()
        self.verification = Verification()

    @property
    def value(self):
        """
        Getter for value
        :return: String
        """
        return self.get("value")

    @value.setter
    @setter_rules(enum=['unknown', 'released', 'development', 'maintenance', 'broken'])
    def value(self, value: str):
        """
        Setter for test case status
        :param value: String
        """
        self.set("value", value)

    @property
    def verification(self):
        """
        Getter for verification
        :return: Verification
        """
        return self.get("verification")

    @verification.setter
    @setter_rules(value_type=Verification)
    def verification(self, value: Verification):
        """
        Setter for test case verification
        :param value: Verification
        """
        self.set("verification", value)
