"""
OpenTMI module for Resource.Item
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Item(BaseApi):
    """
    Item Class
    """

    @property
    def model(self):
        """
        Getter for model
        :return: String
        """
        return self.get("model")

    @model.setter
    @setter_rules()
    def model(self, value):
        """
        Setter for model
        :param value: string
        """
        self.set("model", value)
