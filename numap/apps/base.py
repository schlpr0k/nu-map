'''
nümap applications should subclass the NumapApp.
'''
import sys
import os
import importlib
import logging
try:
    import docopt
except ImportError:  # pragma: no cover - handled in __init__
    docopt = None

# TODO: replace FaceDancerPhy with just FaceDancerApp
try:
    from facedancer import FacedancerUSBApp
except ImportError:  # pragma: no cover - handled in load_phy
    FacedancerUSBApp = None
from numap.utils.ulogger import set_default_handler_level


def _import_greatfet():  # pragma: no cover - simple import helper
    """Import helper that defers importing GreatFET until needed."""

    from greatfet import GreatFET

    return GreatFET


class NumapApp(object):

    def __init__(self, docstring=None):
        if docstring is not None:
            if docopt is None:
                raise ImportError(
                    'docopt is required when providing a CLI docstring to NumapApp'
                )
            self.options = docopt.docopt(docstring)
        else:
            self.options = {}
        self.umap_class_dict = {
            'audio': ('audio', 'Headset'),
            'billboard': ('billboard', 'A billboard, requires USB 2.1 and higher'),
            'cdc_acm': ('cdc_acm', 'Abstract Control Model device (like serial modem)'),
            'cdc_dl': ('cdc_dl', 'Direct Line Control device (like modem)'),
            'ftdi': ('ftdi', 'USB<->RS232 FTDI chip'),
            'hub': ('hub', 'USB hub'),
            'keyboard': ('keyboard', 'Keyboard'),
            'mass_storage': ('mass_storage', 'Disk on key'),
            'mtp': ('mtp', 'Android phone'),
            'printer': ('printer', 'Printer'),
            'smartcard': ('smartcard', 'USB<->smart card interface'),
        }
        self.umap_classes = sorted(self.umap_class_dict.keys())
        self.logger = self.get_logger()
        self.num_processed = 0
        self.fuzzer = None
        self.setup_packet_received = False

    def get_logger(self):
        levels = {
            0: logging.INFO,
            1: logging.DEBUG,
            # verbose is added by numap.__init__ module
            2: logging.VERBOSE,
        }
        verbose = self.options.get('--verbose', 0)
        logger = logging.getLogger('numap')
        if verbose in levels:
            set_default_handler_level(levels[verbose])
        else:
            set_default_handler_level(logging.VERBOSE)
        if self.options.get('--quiet', False):
            set_default_handler_level(logging.WARNING)
        return logger

    def load_phy(self, phy_string):
        phy_string = (phy_string or 'auto').strip()
        phy_selector = phy_string.lower()

        if phy_selector == 'auto':
            phy = self._attempt_greatfet_phy()
            if phy is not None:
                return phy
            return self._create_legacy_facedancer_phy(phy_string)

        if phy_selector.startswith('greatfet'):
            serial = None
            if ':' in phy_string:
                serial = phy_string.split(':', 1)[1].strip() or None
            return self._create_greatfet_phy(serial)

        return self._create_legacy_facedancer_phy(phy_string)

    def _attempt_greatfet_phy(self):
        try:
            return self._create_greatfet_phy()
        except ImportError as exc:
            self.logger.debug('GreatFET support unavailable: %s', exc)
        except Exception as exc:  # pragma: no cover - exercised with real hardware
            self.logger.warning('Failed to initialize GreatFET backend: %s', exc)
        return None

    def _create_greatfet_phy(self, serial=None):
        _import_greatfet()
        if serial:
            os.environ['GREATFET_DEVICE'] = serial
        GreatFET = _import_greatfet()
        kwargs = {}
        if serial is not None:
            kwargs['serial_number'] = serial

        try:
            device = GreatFET(**kwargs)
        except TypeError:
            if serial is not None:
                device = GreatFET(serial)
            else:
                device = GreatFET()
        msg = 'Using GreatFET FaceDancer backend'
        if serial:
            msg += f' (serial: {serial})'
        self.logger.info(msg)
        return self._instantiate_facedancer_app(device=device)

    def _create_legacy_facedancer_phy(self, phy_string):
        if phy_string and phy_string.lower() not in {'', 'auto', 'facedancer', 'fd', 'fd:'} and not phy_string.lower().startswith('fd:'):
            self.logger.info(
                'Using legacy FaceDancer backend for PHY "%s"', phy_string
            )
        return self._instantiate_facedancer_app()

    def _instantiate_facedancer_app(self, device=None):
        if FacedancerUSBApp is None:
            raise ImportError('facedancer is required to load a physical PHY')

        if device is None:
            return FacedancerUSBApp()

        try:
            return FacedancerUSBApp(device=device)
        except TypeError:
            return FacedancerUSBApp(device)

    def load_device(self, dev_name, phy):
        if dev_name in self.umap_classes:
            self.logger.info('Loading USB device %s' % dev_name)
            module_name = self.umap_class_dict[dev_name][0]
            module = importlib.import_module('numap.dev.%s' % module_name)
        else:
            self.logger.info('Loading custom USB device from file: %s' % dev_name)
            dirpath, filename = os.path.split(dev_name)
            modulename = filename[:-3]
            if dirpath in sys.path:
                sys.path.remove(dirpath)
            sys.path.insert(0, dirpath)
            module = __import__(modulename, globals(), locals(), [], -1)
        usb_device = module.usb_device
        kwargs = self.get_user_device_kwargs()
        dev = usb_device(self, phy, **kwargs)
        return dev

    def get_user_device_kwargs(self):
        '''
        if user provides values for the device, get them here
        '''
        kwargs = {}
        self.update_from_user_param('--vid', 'vid', kwargs, 'int')
        self.update_from_user_param('--pid', 'pid', kwargs, 'int')
        return kwargs

    def update_from_user_param(self, flag, arg_name, kwargs, type):
        val = self.options.get(flag, None)
        if val is not None:
            if type == 'int':
                kwargs[arg_name] = int(val, 0)
                self.logger.info('Setting user-supplied %s: %#x' % (arg_name, kwargs[arg_name]))
            else:
                raise Exception('arg type not supported!!')

    def signal_setup_packet_received(self):
        '''
        Signal that we received a setup packet from the host (host is alive)
        '''
        self.setup_packet_received = True

    def should_stop_phy(self):
        '''
        :return: whether phy should stop serving.
        '''
        return False

    def usb_function_supported(self, reason=None):
        '''
        Callback from a USB device, notifying that the current USB device
        is supported by the host.
        By default, do nothing with this information

        :param reason: reason why we decided it is supported (default: None)
        '''
        pass

    def get_mutation(self, stage, data=None):
        '''
        mutation is only needed when fuzzing
        '''
        return None
