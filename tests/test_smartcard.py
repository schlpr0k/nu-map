import os
import struct
import sys
import unittest

STUB_DIR = os.path.join(os.path.dirname(__file__), 'stubs')
if STUB_DIR not in sys.path:
    sys.path.insert(0, STUB_DIR)

from numap.dev.smartcard import (
    R2P_DataBlock,
    R2P_DataRateAndClockFrequency,
    R2P_Escape,
    R2P_Parameters,
    R2P_SlotStatus,
    USBSmartcardInterface,
)


class DummyApp(object):

    def __init__(self):
        self.event_handler = None

    def get_mutation(self, stage, data=None):
        return None

    def usb_function_supported(self, reason=None):
        pass


class DummyPhy(object):

    def __init__(self):
        self.events = []

    def send_on_endpoint(self, ep_num, data):
        self.events.append((ep_num, data))

    def stall_ep0(self):
        self.events.append(('stall', 0))


class SmartcardClassTests(unittest.TestCase):

    def setUp(self):
        self.app = DummyApp()
        self.phy = DummyPhy()
        self.interface = USBSmartcardInterface(self.app, self.phy)
        self.smartcard_class = self.interface.usb_class

    def test_get_clock_frequencies_returns_bytes(self):
        self.interface.clock_frequencies = [0x12345678, 0x9ABCDEF0]
        response = self.smartcard_class.handle_get_clock_frequencies(None)
        self.assertIsInstance(response, bytes)
        payload_length = struct.unpack('<I', response[:4])[0]
        self.assertEqual(payload_length, len(self.interface.clock_frequencies) * 4)
        self.assertEqual(len(response), payload_length + 4)

    def test_get_data_rates_returns_bytes(self):
        self.interface.data_rates = [0x01020304]
        response = self.smartcard_class.handle_get_data_rates(None)
        self.assertIsInstance(response, bytes)
        payload_length = struct.unpack('<I', response[:4])[0]
        self.assertEqual(payload_length, len(self.interface.data_rates) * 4)
        self.assertEqual(len(response), payload_length + 4)


class SmartcardHelperEncodingTests(unittest.TestCase):

    def test_r2p_parameters_encodes_bytes(self):
        data = b'\x01\x02'
        response = R2P_Parameters(0, 1, 2, 3, 4, data)
        expected_header = struct.pack('<BIBBBBB', 0x82, len(data), 0, 1, 2, 3, 4)
        self.assertIsInstance(response, bytes)
        self.assertEqual(response, expected_header + data)

    def test_r2p_datablock_encodes_bytes(self):
        data = b'\xaa\xbb\xcc'
        response = R2P_DataBlock(1, 2, 3, 4, 5, data)
        expected_header = struct.pack('<BIBBBBB', 0x80, len(data), 1, 2, 3, 4, 5)
        self.assertIsInstance(response, bytes)
        self.assertEqual(response, expected_header + data)

    def test_r2p_slotstatus_encodes_bytes(self):
        response = R2P_SlotStatus(2, 3, 4, 5, 6)
        expected = struct.pack('<BIBBBBB', 0x81, 0, 2, 3, 4, 5, 6)
        self.assertIsInstance(response, bytes)
        self.assertEqual(response, expected)

    def test_r2p_escape_encodes_bytes(self):
        data = b'\x10\x20\x30'
        response = R2P_Escape(3, 4, 5, 6, data)
        expected_header = struct.pack('<BIBBBBB', 0x83, len(data), 3, 4, 5, 6, 0)
        self.assertIsInstance(response, bytes)
        self.assertEqual(response, expected_header + data)

    def test_r2p_data_rate_and_clock_frequency_encodes_bytes(self):
        response = R2P_DataRateAndClockFrequency(4, 5, 6, 7, 0x01020304, 0x05060708)
        data = struct.pack('<II', 0x01020304, 0x05060708)
        expected_header = struct.pack('<BIBBBBB', 0x84, len(data), 4, 5, 6, 7, 0)
        self.assertIsInstance(response, bytes)
        self.assertEqual(response, expected_header + data)


if __name__ == '__main__':
    unittest.main()
