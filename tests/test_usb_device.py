import numap.core.usb_device as usb_device


class DummyApp:
    def get_mutation(self, stage, data=None):
        return None

    def usb_function_supported(self, reason=None):
        pass


class DummyPhy:
    def __init__(self):
        self.connected_device = None
        self.disconnected = False

    def connect(self, device):
        self.connected_device = device

    def disconnect(self):
        self.disconnected = True

    def send_on_endpoint(self, ep, data):
        pass

    def ack_status_stage(self):
        pass


def _make_device(monkeypatch):
    # Ensure facedancer internals are not exercised during the test by replacing
    # the BaseUSBDevice initializer with a lightweight stub.
    monkeypatch.setattr(
        usb_device.BaseUSBDevice,
        '__init__',
        lambda self, *args, **kwargs: None,
    )
    phy = DummyPhy()
    dev = usb_device.USBDevice(
        app=DummyApp(),
        phy=phy,
        device_class=0,
        device_subclass=0,
        protocol_rel_num=0,
        max_packet_size_ep0=8,
        vendor_id=0,
        product_id=0,
        device_rev=0,
        manufacturer_string='n',
        product_string='n',
        serial_number_string='n',
    )
    return dev, phy


def test_usb_device_connect_passes_backend(monkeypatch):
    dev, phy = _make_device(monkeypatch)
    called = []

    def fake_connect(self, backend=None):
        called.append(backend)

    monkeypatch.setattr(usb_device.BaseUSBDevice, 'connect', fake_connect)
    dev.connect()
    assert called == [phy]


def test_usb_device_connect_falls_back_without_backend(monkeypatch):
    dev, phy = _make_device(monkeypatch)
    called = []

    def legacy_connect(self):
        called.append('legacy')

    monkeypatch.setattr(usb_device.BaseUSBDevice, 'connect', legacy_connect)
    dev.connect()
    assert called == ['legacy']


def test_usb_device_connect_overrides_facedancer_factory(monkeypatch):
    dev, phy = _make_device(monkeypatch)
    import facedancer

    original = facedancer.FacedancerUSBApp
    created = []

    def fake_connect(self, backend=None):
        created.append(facedancer.FacedancerUSBApp())

    monkeypatch.setattr(usb_device.BaseUSBDevice, 'connect', fake_connect)
    dev.connect()
    assert created == [phy]
    assert facedancer.FacedancerUSBApp is original


def test_usb_device_connect_overrides_factory_with_kwargs(monkeypatch):
    dev, phy = _make_device(monkeypatch)
    import facedancer

    created = []

    def fake_connect(self, backend=None):
        created.append(facedancer.FacedancerUSBApp(verbose=True))

    monkeypatch.setattr(usb_device.BaseUSBDevice, 'connect', fake_connect)
    dev.connect()
    assert created == [phy]
