import os
import unittest
from opentmi_client.api import Result, Execution, File, Dut, Provider


class TestResult(unittest.TestCase):
    def test_construct(self):
        result = Result()
        result.tcid = 'test'
        self.assertIsInstance(result, Result)
        self.assertEqual(result.tcid, 'test')
        self.assertEqual(result.data, {'tcid': 'test'})

    def test_verdict(self):
        result = Result()
        result.verdict = 'pass'
        self.assertEqual(result.verdict, 'pass')

    def test_execution(self):
        result = Result()
        result.execution.duration = 12.0
        self.assertEqual(result.execution.duration, 12.0)
        result.execution = Execution()
        result.execution.note = 'notes'
        self.assertEqual(result.execution.note, 'notes')
        self.assertEqual(result.execution.duration, None)

    def test_execution_metadata(self):
        result = Result()
        result.execution.metadata['key'] = 'value'
        self.assertEqual(result.execution.metadata.get('key'), 'value')

    def test_dut(self):
        result = Result()
        dut = Dut()
        dut.model = 'abc'
        dut.serial_number = '123'
        dut.type = 'hw'
        dut.vendor = 'some'
        provider = Provider()
        provider.name = 'stub'
        provider.ver = '1.0.0'
        provider.id = '0'
        dut.provider = provider
        result.execution.append_dut(dut)
        self.assertEqual(result.execution.duts[0].model, 'abc')
        self.assertEqual(result.execution.duts[0].serial_number, '123')
        self.assertEqual(result.execution.duts[0].type, 'hw')
        self.assertEqual(result.execution.duts[0].vendor, 'some')
        self.assertEqual(result.execution.duts[0].provider.name, 'stub')
        self.assertEqual(result.execution.duts[0].provider.ver, '1.0.0')
        self.assertEqual(result.execution.duts[0].provider.id, '0')
        self.assertEqual(result.data, {
            'exec': {'duts': [{
                'model': 'abc',
                'provider': {'id': '0', 'name': 'stub', 'ver': '1.0.0'},
                'sn': '123',
                'type': 'hw',
                'vendor': 'some'
            }]
        }})

    def test_file(self):
        result = Result()
        log_file = File()
        log_file.name = "stderr.log"
        self.assertEqual(log_file.name, "stderr.log")
        log_file.set_file_data("test")
        self.assertEqual(log_file.encoding, "raw")
        self.assertEqual(str(log_file), "stderr.log")
        self.assertEqual(log_file.raw_data, "test")
        result.execution.append_log(log_file)
        self.assertEqual(len(result.execution.logs), 1)
        self.assertEqual(result.execution.logs[0], log_file)

    def test_from_dictionary(self):
        def reducer_func(_result, value, key):
            if key == "result":
                _result.verdict = value.lower()
            elif key == "test.name":
                _result.tcid = value
            return _result
        result = Result.from_dict({"result": "PASS", "test": {"name": "hello"}}, reducer=reducer_func)
        self.assertEqual(result.data, {"exec": {"verdict": "pass"}, "tcid": "hello"})

    def test_from_junit(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        junit_file = os.path.join(dir_path, "../test/data/junit_simple.xml")
        results = Result.from_junit_file(junit_file)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].tcid, "should default path to an empty string")
        self.assertEqual(results[0].verdict, "fail")
        self.assertEqual(results[1].verdict, "skip")
        self.assertEqual(results[2].verdict, "pass")

