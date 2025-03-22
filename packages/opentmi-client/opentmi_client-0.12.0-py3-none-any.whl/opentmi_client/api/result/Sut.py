"""
OpenTMI SUT (Software under test) module
"""
from opentmi_client.utils.Base import BaseApi
from opentmi_client.utils.decorators import setter_rules


class Sut(BaseApi):
    """
    SUT (Software Under Test) class
    """

    def __init__(self):
        super(Sut, self).__init__()
        self.set("cut", [])
        self.set("fut", [])

    @property
    def ref(self):
        """
        Getter for reference
        :return: String
        """
        return self.get("ref")

    @ref.setter
    @setter_rules()
    def ref(self, value):
        """
        Setter for reference
        :param value: String
        """
        self.set("ref", value)

    @property
    def cut(self):
        """
        Getter for Component Under Test
        :return: String
        """
        return self.get("cut")

    @setter_rules()
    def append_cut(self, value):
        """
        Append one component under test
        :param value: String
        """
        self.cut.append(value)

    @property
    def fut(self):
        """
        Getter for Feature Under Test
        :return: String
        """
        return self.get("fut")

    @setter_rules()
    def append_fut(self, value):
        """
        Append one feature under test
        :param value: String
        """
        self.get("fut").append(value)

    @property
    def git_url(self):
        """
        Getter for git url
        :return: String
        """
        return self.get("gitUrl")

    @git_url.setter
    @setter_rules()
    def git_url(self, value):
        """
        Setter for git url
        :param value: String
        """
        self.set("gitUrl", value)

    @property
    def build_sha1(self):
        """
        Getter for git build file sha1
        :return: String
        """
        return self.get("buildSha1")

    @build_sha1.setter
    @setter_rules()
    def build_sha1(self, value):
        """
        Setter for git build file sha1
        :param value: String
        """
        self.set("buildSha1", value)

    @property
    def commit_id(self):
        """
        Getter for git commit id
        :return: String
        """
        return self.get("commitId")

    @commit_id.setter
    @setter_rules()
    def commit_id(self, value):
        """
        Setter for git commit id
        :param value: String
        """
        self.set("commitId", value)

    @property
    def branch(self):
        """
        Getter for git commit branch
        :return: String
        """
        return self.get("branch")

    @branch.setter
    @setter_rules()
    def branch(self, value):
        """
        Setter for git branch
        :param value: String
        """
        self.set("branch", value)

    @property
    def tag(self):
        """
        Getter for git commit id
        :return: String
        """
        return self.get("tag")

    @tag.setter
    @setter_rules(list, each_type=str)
    def tag(self, value):
        """
        Setter for git commit id
        :param value: String
        """
        self.set("tag", value)

# buildName: {type: String},
# buildDate: {type: Date},
# buildUrl: {type: String, default: ''},
# href: {type: String},
