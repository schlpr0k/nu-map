'''
USB Configuration class.
Each instance represents a single USB configuration.
In most cases it should not be subclassed.
'''
import struct
from numap.core.usb_base import USBBaseActor
from numap.core.usb import DescriptorType
from numap.fuzz.helpers import mutable

from facedancer.USBConfiguration import USBConfiguration as BaseUSBConfiguration

class USBConfiguration(USBBaseActor, BaseUSBConfiguration):

    name = 'Configuration'

    # Those attributes can be ORed
    # At least one should be selected
    ATTR_BASE = 0x80
    ATTR_SELF_POWERED = ATTR_BASE | 0x40
    ATTR_REMOTE_WAKEUP = ATTR_BASE | 0x20

    def __init__(
        self, app, phy,
        index, string, interfaces,
        attributes=ATTR_SELF_POWERED,
        max_power=0x32,
    ):
        '''
        :param app: nümap application
        :param phy: Physical connection
        :param index: configuration index (starts from 1)
        :param string: configuration string
        :param interfaces: list of interfaces for this configuration
        :param attributes: configuratioin attributes. one or more of USBConfiguration.ATTR_* (default: ATTR_SELF_POWERED)
        :param max_power: maximum power consumption of this configuration (default: 0x32)
        '''

        USBBaseActor.__init__(self, app, phy)
        BaseUSBConfiguration.__init__(self, index, string, interfaces, attributes, max_power)
        self.configuration_string = string
        self.configuration_string_index = 0
        self.interfaces = interfaces

    @mutable('configuration_descriptor')
    def get_descriptor(self, usb_type='fullspeed', valid=False):
        interface_bytes = b''.join(
            interface.get_descriptor(usb_type, valid) for interface in self.interfaces
        )
        total_length = 9 + len(interface_bytes)
        descriptor = struct.pack(
            '<BBHBBBBB',
            9,  # length of descriptor
            DescriptorType.configuration,
            total_length,
            len(self.interfaces),
            self.index,
            self.configuration_string_index,
            self.attributes,
            self.max_power,
        )
        return descriptor + interface_bytes

    def get_other_speed_descriptor(self):
        return self.get_descriptor('highspeed')
