"""Tests for :mod:`numap.core.usb_configuration`."""

from __future__ import annotations

from numap.core import usb_configuration
from numap.core.usb_configuration import USBConfiguration


class DummyApp:
    def get_mutation(self, stage, data=None):  # pragma: no cover - helper
        return None

    def usb_function_supported(self, reason=None):  # pragma: no cover - helper
        return None


class DummyPhy:
    def send_on_endpoint(self, ep, data):  # pragma: no cover - helper
        return None

    def stall_ep0(self):  # pragma: no cover - helper
        return None


class DummyInterface:
    def __init__(self):
        self.configuration = None

    def get_descriptor(self, usb_type='fullspeed', valid=False):  # pragma: no cover - helper
        return b''

    def set_configuration(self, config):
        self.configuration = config


def _make_configuration():
    interface = DummyInterface()
    config = USBConfiguration(DummyApp(), DummyPhy(), 1, 'cfg', [interface])
    return config, interface


def test_set_device_assigns_configuration_to_interfaces():
    config, interface = _make_configuration()
    device = object()

    config.set_device(device)

    assert config.device is device
    assert interface.configuration is config


def test_set_device_invokes_facedancer_backend(monkeypatch):
    calls = []

    def fake_set_device(self, device):
        calls.append((self, device))

    monkeypatch.setattr(
        usb_configuration.BaseUSBConfiguration, 'set_device', fake_set_device, raising=False
    )

    config, _ = _make_configuration()
    device = object()

    config.set_device(device)

    assert calls == [(config, device)]
