from .USBDevice import USBDevice

__all__ = ['FacedancerUSBApp', 'USBDevice']


class FacedancerUSBApp(object):
    def __init__(self, *args, **kwargs):
        self.connected_device = None
        self.args = args
        self.kwargs = kwargs
        self.device = kwargs.get('device')
        if self.device is None and args:
            self.device = args[0]

    def connect(self, device):
        self.connected_device = device

    def disconnect(self):
        self.connected_device = None

    def send_on_endpoint(self, ep, data):
        pass
