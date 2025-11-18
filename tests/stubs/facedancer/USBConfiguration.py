class USBConfiguration(object):
    def __init__(self, index, string, interfaces, attributes, max_power):
        self.index = index
        self.string = string
        self.interfaces = interfaces
        self.attributes = attributes
        self.max_power = max_power

    def set_device(self, device):
        for interface in self.interfaces:
            interface.set_configuration(self)
