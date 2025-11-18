import asyncio
from types import SimpleNamespace

import numap.apps.scan as scan
from numap.apps.scan import NumapScanApp


class DummyLogger:
    def __init__(self):
        self.error_messages = []

    def always(self, *args, **kwargs):  # pragma: no cover - debug helper
        return None

    def info(self, *args, **kwargs):  # pragma: no cover - debug helper
        return None

    def error(self, message, *args):
        if args:
            message = message % args
        self.error_messages.append(message)


class TimeoutDevice:
    def __init__(self):
        self.disconnect_called = False

    def connect(self):
        return None

    def run(self):
        return asyncio.sleep(0.1)

    def disconnect(self):
        self.disconnect_called = True


class TimeoutScanApp(NumapScanApp):
    def __init__(self):
        super().__init__(options=None)
        self.options['--phy'] = 'stub'
        self.timeout_seconds = 0.01
        self.umap_classes = ['timeout-device']
        self.logger = DummyLogger()
        self._phy = SimpleNamespace(disconnect=lambda: setattr(self, 'phy_disconnected', True))
        self.device = None

    def load_phy(self, phy_string):
        return self._phy

    def load_device(self, device_name, phy):
        self.device = TimeoutDevice()
        return self.device


def test_scan_app_times_out_and_disconnects(monkeypatch):
    app = TimeoutScanApp()
    monkeypatch.setattr(scan.time, 'sleep', lambda _seconds: None)

    app.run()

    assert app.device.disconnect_called
    assert getattr(app, 'phy_disconnected', False)
    assert any('Timed out' in message for message in app.logger.error_messages)
