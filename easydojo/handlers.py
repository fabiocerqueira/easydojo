from clint.textui import puts, colored, indent
from watchdog.events import FileSystemEventHandler
import yaml

import subprocess
import os
import glob
import sys


class DojoEventHandler(FileSystemEventHandler):
    """ Displays only the file that is being changed """

    def __init__(self, handlers, *args, **kwargs):
        super(DojoEventHandler, self).__init__(*args, **kwargs)
        self.handlers = [ConsoleHandler()]
        for h in handlers:
            handler = globals().get('{0}Handler'.format(h))
            if (handler and issubclass(handler, BaseHandler) and
                handler is not BaseHandler and
                handler is not ConsoleHandler):
                self.handlers.append(handler())
            else:
                puts(colored.red("{0} isn't a handler".format(h)))
        self.handlers = list(set(self.handlers))
        puts('EasyDojo running...')

    def on_modified(self, event):
        if event.is_directory:
            return
        filename = os.path.basename(event.src_path)
        config_file = os.path.join(os.getcwd(), '.easydojo.yaml')
        with open(config_file) as stream:
            config = yaml.load(stream)
        if filename not in config['files']:
            return
        puts('Modified file {name}'.format(name=filename))
        puts('Running test runner:')
        puts(config['test_runner'])
        cmd = config['test_runner'].split()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return_code = proc.wait()
        for h in self.handlers:
            h.execute(event, return_code, proc)


class BaseHandler(object):

    def execute(self, event, return_code, proc):
        return event, return_code, proc


class ConsoleHandler(BaseHandler):
    """ Displays tests results on console, It's default. """

    def execute(self, event, return_code, proc):
        if return_code:
            quote = colored.red('||')
        else:
            quote = colored.green('||')
        with indent(4, quote=quote):
            puts(proc.stderr.read())
            puts(proc.stdout.read())
        return super(ConsoleHandler, self).execute(event, return_code, proc)


class MacNotifyHandler(BaseHandler):
    """ Displays tests results on console and a Mac Desktop notification """

    def execute(self, event, return_code, proc):
        try:
            from pync import Notifier
        except ImportError:
            puts(colored.red('Module pync not found, use: pip install pync'))
            sys.exit(1)
        if return_code:
            message = 'Error!'
        else:
            message = "Success!"
        Notifier.notify(message, title="EasyDojo")
        return super(MacNotifyHandler, self).execute(event, return_code, proc)


class ArduinoHandler(BaseHandler):
    """ Send a serial command to arduino with tests results """

    def __init__(self):
        try:
            import serial
        except ImportError:
            puts(colored.red('Module pyserial not found, use: pip install pyserial'))
            sys.exit(1)
        try:
            arduino_path = (glob.glob('/dev/ttyUSB*') + glob.glob('/dev/tty.usb*'))[0]
        except IndexError:
            puts(colored.red('Could not find an arduino device'))
            sys.exit(1)
        self.arduino = serial.Serial(arduino_path, 9600)

    def execute(self, event, return_code, proc):
        if return_code:
            message = 'E'
        else:
            message = "S"
        self.arduino.write(message)
        return super(ArduinoHandler, self).execute(event, return_code, proc)

    def __del__(self):
        if hasattr(self, 'arduino'):
            self.arduino.close()
