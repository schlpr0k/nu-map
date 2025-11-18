class USBConfiguration:
    def __init__(self, index, string, interfaces, attributes, max_power):
        self.index = index
        self.configuration_string = string
        self.configuration_string_index = 0
        self.interfaces = interfaces
        self.attributes = attributes
        self.max_power = max_power
        self.device = None

    def set_device(self, device):
        self.device = device
