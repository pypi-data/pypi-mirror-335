import unittest
from opentmi_client.api.testcase.Testcase import Testcase
from opentmi_client.api.testcase.Compatible import Compatible
from opentmi_client.api.testcase.Status import Status
from opentmi_client.api.testcase.Execution import Execution
from opentmi_client.api.testcase.OtherInfo import OtherInfo


class TestTestcase(unittest.TestCase):
    def test_construct(self):
        test = Testcase(tcid="")
        self.assertIsInstance(test, Testcase)
        self.assertEqual(test.data, {})

    def test_str(self):
        test = Testcase(tcid="id")
        self.assertEqual(str(test), "id")

    def test_properties(self):
        test = Testcase(tcid="abc")
        self.assertEqual(test.tcid, "abc")
        self.assertIsInstance(test.execution, Execution)
        self.assertIsInstance(test.other_info, OtherInfo)
        self.assertIsInstance(test.status, Status)
        self.assertIsInstance(test.compatible, Compatible)
        test.execution.skip.value = True
        self.assertTrue(test.execution.skip.value)
        test.execution.skip.reason = "note"
        self.assertEqual(test.execution.skip.reason, "note")
        test.other_info.title = "aa"
        self.assertEqual(test.other_info.title, "aa")
        test.other_info.description = "desc"
        self.assertEqual(test.other_info.description, "desc")
        test.other_info.type = "installation"
        self.assertEqual(test.other_info.type, "installation")
        test.other_info.keywords = ["aa"]
        self.assertEqual(test.other_info.keywords, ["aa"])
        test.status.value = "released"
        self.assertEqual(test.status.value, "released")
        test.status.verification.value = True
        self.assertTrue(test.status.verification.value)
        self.assertDictEqual(test.data, {
            "tcid": "abc",
            "execution": {
                "skip": {
                    "value": True,
                    "reason": "note"
                }
            },
            "status": {
                "value": "released",
                "verification": {
                    "value": True
                }
            },
            "other_info": {
                "title": "aa",
                "description": "desc",
                "type": "installation",
                "keywords": ["aa"]
            }
        })
