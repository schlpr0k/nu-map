class USBDevice(object):
    def __init__(
        self, phy, usb_class, device_subclass, protocol_rel_num, max_packet_size_ep0,
        vendor_id, product_id, device_rev, manufacturer_string, product_string,
        serial_number_string, configurations, descriptors
    ):
        self.phy = phy
        self.usb_class = usb_class
        self.device_subclass = device_subclass
        self.protocol_rel_num = protocol_rel_num
        self.max_packet_size_ep0 = max_packet_size_ep0
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device_rev = device_rev
        self.manufacturer_string = manufacturer_string
        self.product_string = product_string
        self.serial_number_string = serial_number_string
        self.configurations = configurations
        self.descriptors = descriptors

    def connect(self, device=None):
        pass

    def disconnect(self):
        pass

    def ack_status_stage(self):
        pass
