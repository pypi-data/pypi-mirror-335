"""
OpenTMI module for Resource.hw
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Hardware(BaseApi):
    """
    Hardware Class
    """

    @property
    def serial_number(self):
        """
        Getter for serial_number
        :return: String
        """
        return self.get("sn")

    @serial_number.setter
    @setter_rules()
    def serial_number(self, value):
        """
        Setter for serial_number
        :param value: string
        """
        self.set("sn", value)

    @property
    def hwid(self):
        """
        Getter for hwid
        :return: String
        """
        return self.get("hwid")

    @hwid.setter
    @setter_rules()
    def hwid(self, value):
        """
        Setter for hwid
        :param value: string
        """
        self.set("hwid", value)
