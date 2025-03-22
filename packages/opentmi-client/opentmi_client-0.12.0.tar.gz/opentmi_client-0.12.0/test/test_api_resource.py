import unittest
from opentmi_client.api.resource.Resource import Resource
from opentmi_client.api.resource.Status import Status
from opentmi_client.api.resource.Item import Item
from opentmi_client.api.resource.Hardware import Hardware


class TestResource(unittest.TestCase):
    def test_construct(self):
        resource = Resource()
        self.assertIsInstance(resource, Resource)
        self.assertEqual(resource.data, {})

    def test_str(self):
        res = Resource(name="abc")
        self.assertEqual(str(res), "abc")

    def test_properties(self):
        res = Resource(name="abc")
        self.assertEqual(res.name, "abc")
        res.type = 'dut'
        self.assertEqual(res.type, 'dut')
        self.assertIsInstance(res.item, Item)
        self.assertIsInstance(res.status, Status)
        self.assertIsInstance(res.hardware, Hardware)
        res.item.model = 'aa'
        self.assertEqual(res.item.model, 'aa')
        res.status.value = 'active'
        self.assertEqual(res.status.value, 'active')

        res.status.availability = 'free'
        self.assertEqual(res.status.availability, 'free')

        res.status.note = 'node'
        self.assertEqual(res.status.note, 'node')

        res.hardware.hwid = '123'
        self.assertEqual(res.hardware.hwid, '123')


        res.hardware.serial_number = '12'
        self.assertEqual(res.hardware.serial_number, '12')

        self.assertDictEqual(res.data, {
            'name': 'abc',
            'type': 'dut',
            'item': {
                'model': 'aa'
            },
            'status': {
                'value': 'active',
                'note': 'node',
                'availability': 'free'
            },
            'hw': {
                'hwid': '123',
                'sn': '12'
            }
        })
