"""
OpenTMI module for Resource
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules
from opentmi_client.api.resource.Item import Item
from opentmi_client.api.resource.Status import Status
from opentmi_client.api.resource.Hardware import Hardware


class Resource(BaseApi):
    """
    Resource Class
    """

    def __init__(self, name=""):
        """
        Constructor for Resource
        """
        super().__init__()
        self.name = name
        self.item = Item()
        self.status = Status()
        self.hardware = Hardware()

    def __str__(self):
        return self.name

    @property
    def name(self):
        """
        Getter for name
        :return: String
        """
        return self.get("name")

    @name.setter
    @setter_rules()
    def name(self, value):
        """
        Setter for name
        :param value: string
        """
        self.set("name", value)

    @property
    def type(self):
        """
        Getter for type
        :return: String
        """
        return self.get("type")

    @type.setter
    @setter_rules(enum=[
        'system',
        'dut',
        'instrument',
        'accessories',
        'computer',
        'room'
    ])
    def type(self, value):
        """
        Setter for type
        :param value: string
        """
        self.set("type", value)

    @property
    def item(self):
        """
        Getter for item
        :return: Item
        """
        return self.get("item")

    @item.setter
    @setter_rules(Item)
    def item(self, value):
        """
        Setter for item
        :param value: Item
        """
        self.set("item", value)

    @property
    def status(self) -> Status:
        """
        Getter for status
        :return: Status
        """
        return self.get("status")

    @status.setter
    @setter_rules(Status)
    def status(self, value):
        """
        Setter for status
        :param value: Status
        """
        self.set("status", value)

    @property
    def hardware(self) -> Hardware:
        """
        Getter for hardware
        :return: Hardware
        """
        return self.get("hw")

    @hardware.setter
    @setter_rules(Hardware)
    def hardware(self, value):
        """
        Setter for hardware
        :param value: Hardware
        """
        self.set("hw", value)
