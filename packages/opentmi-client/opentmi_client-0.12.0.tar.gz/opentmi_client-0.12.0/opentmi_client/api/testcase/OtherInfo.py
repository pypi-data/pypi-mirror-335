""" OpenTMI OtherInfo module """
# Internal imports
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class OtherInfo(BaseApi):
    """ OtherInfo class """

    @property
    def title(self):
        """
        Getter for title
        :return: String
        """
        return self.get("title")

    @title.setter
    @setter_rules()
    def title(self, value: str):
        """
        Setter for test case title
        :param value: String
        """
        self.set("title", value)

    @property
    def type(self):
        """
        Getter for type
        :return: String
        """
        return self.get("type")

    @type.setter
    @setter_rules(enum=[
        'installation',
        'compatibility',
        'smoke',
        'regression',
        'acceptance',
        'alpha',
        'beta',
        'stability',
        'functional',
        'destructive',
        'performance',
        'reliability'])
    def type(self, value: str):
        """
        Setter for test case type
        :param value: String
        """
        self.set("type", value)

    @property
    def purpose(self):
        """
        Getter for purpose
        :return: String
        """
        return self.get("purpose")

    @purpose.setter
    @setter_rules()
    def purpose(self, value: str):
        """
        Setter for test case purpose
        :param value: String
        """
        self.set("purpose", value)

    @property
    def description(self):
        """
        Getter for description
        :return: String
        """
        return self.get("description")

    @description.setter
    @setter_rules()
    def description(self, value: str):
        """
        Setter for test case description
        :param value: String
        """
        self.set("description", value)

    @property
    def layer(self):
        """
        Getter for layer
        :return: String
        """
        return self.get("layer")

    @layer.setter
    @setter_rules(enum=['L1', 'L2', 'L3', 'unknown'])
    def layer(self, value: str):
        """
        Setter for test case layer
        :param value: String
        """
        self.set("layer", value)

    @property
    def components(self):
        """
        Getter for components
        :return: list<str>
        """
        return self.get("components")

    @components.setter
    @setter_rules(value_type=list, each_type=str)
    def components(self, value: list):
        """
        Setter for test case components
        :param value: String
        """
        self.set("components", value)

    @property
    def features(self):
        """
        Getter for features
        :return: list<str>
        """
        return self.get("features")

    @features.setter
    @setter_rules(value_type=list, each_type=str)
    def features(self, value: list):
        """
        Setter for test case features
        :param value: String
        """
        self.set("features", value)

    @property
    def keywords(self):
        """
        Getter for keywords
        :return: list<str>
        """
        return self.get("keywords")

    @keywords.setter
    @setter_rules(value_type=list, each_type=str)
    def keywords(self, value: list):
        """
        Setter for test case keywords
        :param value: String
        """
        self.set("keywords", value)
