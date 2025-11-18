class FacedancerUSBApp(object):
    def __init__(self, *args, **kwargs):
        self.connected_device = None

    def connect(self, device):
        self.connected_device = device

    def disconnect(self):
        self.connected_device = None

    def send_on_endpoint(self, ep, data):
        pass
