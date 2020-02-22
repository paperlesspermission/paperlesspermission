"""Test module for utils.py"""

from io import BytesIO, StringIO
from django.test import TestCase
from paperlesspermission.utils import bytes_io_to_string_io, bytes_io_to_tsv_dict_reader


class BytesIOToStringIOTestCase(TestCase):
    b_value = b'Test String'
    value = 'Test String'

    def test_bytes_io_to_string_io(self):
        test = bytes_io_to_string_io(BytesIO(self.b_value)).getvalue()
        expected = StringIO(self.value).getvalue()
        self.assertEqual(test, expected)


class BytesIOToTSVDictReader(TestCase):
    # ID    TEST_VALUE  SAMPLE
    # 1     Apple       Granny
    # 2     Smith       Hare
    # a     Adams       Ferret #1
    b_value = b'ID\tTEST_VALUE\tSAMPLE\n1\tApple\tGranny\n2\tSmith\tHare\na\tAdams\tFerret #1'
    result = [{'ID': '1', 'TEST_VALUE': 'Apple', 'SAMPLE': 'Granny'},
              {'ID': '2', 'TEST_VALUE': 'Smith', 'SAMPLE': 'Hare'},
              {'ID': 'a', 'TEST_VALUE': 'Adams', 'SAMPLE': 'Ferret #1'}]

    def test_bytes_io_to_tsv_dict_reader(self):
        i = 0
        for row in bytes_io_to_tsv_dict_reader(BytesIO(self.b_value)):
            expected = self.result[i]
            self.assertDictEqual(row, expected)
            i += 1