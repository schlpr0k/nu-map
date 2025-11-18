import importlib
import os
import sys

import numap.apps.base as base
from numap.apps.base import NumapApp


class SimpleApp(NumapApp):
    def __init__(self):
        super(SimpleApp, self).__init__(docstring=None)


def test_load_phy_greatfet_with_serial(monkeypatch):
    monkeypatch.delenv('GREATFET_DEVICE', raising=False)
    monkeypatch.delenv('BACKEND', raising=False)
    app = SimpleApp()
    phy = app.load_phy('greatfet:ABC123')
    assert os.environ['GREATFET_DEVICE'] == 'ABC123'
    assert os.environ['BACKEND'] == 'greatfet'
    assert phy.device.serial_number == 'ABC123'
    app = SimpleApp()
    phy = app.load_phy('greatfet:ABC123')
    assert phy.device.serial_number == 'ABC123'


def test_load_phy_auto_falls_back(monkeypatch):
    def raising_import():
        raise ImportError('missing greatfet')

    monkeypatch.setattr(base, '_import_greatfet', raising_import)
    app = SimpleApp()
    phy = app.load_phy('auto')
    assert getattr(phy, 'device', None) is None


def test_load_phy_sets_backend_before_import(monkeypatch):
    monkeypatch.delenv('BACKEND', raising=False)
    monkeypatch.delenv('GREATFET_DEVICE', raising=False)
    monkeypatch.delitem(sys.modules, 'facedancer', raising=False)
    base.FacedancerUSBApp = None

    app = SimpleApp()
    phy = app.load_phy('greatfet:SERIAL42')
    assert phy.device.serial_number == 'SERIAL42'

    facedancer = importlib.import_module('facedancer')
    assert facedancer.BACKEND_ENV_AT_IMPORT == 'greatfet'
    assert facedancer.GREATFET_DEVICE_ENV_AT_IMPORT == 'SERIAL42'
