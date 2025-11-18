import numap.apps.base as base
from numap.apps.base import NumapApp


class SimpleApp(NumapApp):
    def __init__(self):
        super(SimpleApp, self).__init__(docstring=None)


def test_load_phy_greatfet_with_serial(monkeypatch):
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
