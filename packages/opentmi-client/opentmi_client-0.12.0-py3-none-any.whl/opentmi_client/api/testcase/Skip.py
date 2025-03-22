""" OpenTMI module """
# Internal imports
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Skip(BaseApi):
    """ Skip class """

    @property
    def value(self):
        """
        Getter for skip value
        :return: bool
        """
        return self.get("value")

    @value.setter
    @setter_rules(value_type=bool)
    def value(self, value: bool):
        """
        Setter for test case skip value
        :param value: bool
        """
        self.set("value", value)

    @property
    def reason(self):
        """
        Getter for skip reason
        :return: str
        """
        return self.get("reason")

    @reason.setter
    @setter_rules()
    def reason(self, value: str):
        """
        Setter for test case skip reason
        :param value: bool
        """
        self.set("reason", value)
