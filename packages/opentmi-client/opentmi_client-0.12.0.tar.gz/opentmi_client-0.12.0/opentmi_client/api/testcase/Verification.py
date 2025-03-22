""" OpenTMI module """
# Internal imports
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Verification(BaseApi):
    """ Execution class """

    @property
    def value(self):
        """
        Getter for value
        :return: bool
        """
        return self.get("value")

    @value.setter
    @setter_rules(bool)
    def value(self, value: bool):
        """
        Setter for test case verification value
        :param value: bool
        """
        self.set("value", value)
