'''
Scan device support in USB host

Usage:
    numapscan [-P=PHY_INFO] [-t SECONDS] [-q] [-v ...]

Options:
    -P --phy PHY_INFO           physical layer info, see list below
    -t --timeout SECONDS        maximum time to wait for a host response [default: 5]
    -v --verbose                verbosity level
    -q --quiet                  quiet mode. only print warning/error messages

Physical layer:
    greatfet[:serial]       use a GreatFET board (auto-detects when serial omitted)
    facedancer              use legacy FaceDancer hardware
    gadgetfs                use gadgetfs (requires mounting of gadgetfs beforehand)

Example:
    numapscan -P greatfet -q
'''
import asyncio
import inspect
import time
import traceback
from numap.apps.base import NumapApp


class NumapScanApp(NumapApp):

    def __init__(self, options):
        super(NumapScanApp, self).__init__(options)
        self.current_usb_function_supported = False
        self.start_time = 0
        timeout_opt = self.options.get('--timeout', 5)
        try:
            self.timeout_seconds = float(timeout_opt)
        except (TypeError, ValueError) as exc:
            raise ValueError('Timeout must be a numeric value in seconds') from exc

    def usb_function_supported(self, reason=None):
        '''
        Callback from a USB device, notifying that the current USB device
        is supported by the host.

        :param reason: reason why we decided it is supported (default: None)
        '''
        self.current_usb_function_supported = True

    def run(self):
        self.logger.always('Scanning host for supported devices')
        phy = self.load_phy(self.options['--phy'])
        supported = []
        for device_name in self.umap_classes:
            self.logger.always('Testing support: %s' % (device_name))
            try:
                self.start_time = time.time()
                device = self.load_device(device_name, phy)
                device.connect()
                result = device.run()
                if inspect.isawaitable(result):
                    asyncio.run(result)
                device.disconnect()
            except:
                self.logger.error(traceback.format_exc())
            phy.disconnect()
            if self.current_usb_function_supported:
                self.logger.always('Device is SUPPORTED')
                supported.append(device_name)
            self.current_usb_function_supported = False
            time.sleep(2)
        if len(supported):
            self.logger.always('---------------------------------')
            self.logger.always('Found %s supported device(s):' % (len(supported)))
            for i, device_name in enumerate(supported):
                self.logger.always('%d. %s' % (i + 1, device_name))

    def should_stop_phy(self):
        # if self.current_usb_function_supported:
        #     self.logger.debug('Current USB device is supported, stopping phy')
        #     return True
        stop_phy = False
        passed = int(time.time() - self.start_time)
        if passed > self.timeout_seconds:
            self.logger.info('have been waiting long enough (over %d secs.), disconnect' % (passed))
            stop_phy = True
        return stop_phy


def main():
    app = NumapScanApp(__doc__)
    app.run()


if __name__ == '__main__':
    main()
