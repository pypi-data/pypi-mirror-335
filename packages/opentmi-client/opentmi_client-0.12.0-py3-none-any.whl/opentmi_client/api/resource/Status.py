"""
OpenTMI module for Resource.status
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Status(BaseApi):
    """
    Status Class
    """

    @property
    def value(self):
        """
        Getter for value
        :return: String
        """
        return self.get("value")

    @value.setter
    @setter_rules(enum=[
        'active',
        'maintenance',
        'storage',
        'broken'
    ])
    def value(self, value):
        """
        Setter for value
        :param value: string
        """
        self.set("value", value)

    @property
    def note(self):
        """
        Getter for note
        :return: String
        """
        return self.get("note")

    @note.setter
    @setter_rules()
    def note(self, value):
        """
        Setter for note
        :param value: string
        """
        self.set("note", value)

    @property
    def availability(self):
        """
        Getter for availability
        :return: str
        """
        return self.get("availability")

    @availability.setter
    @setter_rules(enum=['free', 'reserved'])
    def availability(self, value):
        """
        Setter for availability
        :param value: string
        """
        self.set("availability", value)
