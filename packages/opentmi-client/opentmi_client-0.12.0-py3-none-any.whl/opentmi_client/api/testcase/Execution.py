""" OpenTMI module """
# Internal imports
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules
from opentmi_client.api.testcase.Skip import Skip


class Execution(BaseApi):
    """ Execution class """
    def __init__(self):
        """ Constructor for Execution """
        super().__init__()
        self.skip = Skip()

    @property
    def skip(self):
        """
        Getter for skip
        :return: Skip
        """
        return self.get("skip")

    @skip.setter
    @setter_rules(value_type=Skip)
    def skip(self, value: Skip):
        """
        Setter for test case skip
        :param value: Skip
        """
        self.set("skip", value)
