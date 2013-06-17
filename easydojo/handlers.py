from clint.textui import puts, colored, indent
from watchdog.events import FileSystemEventHandler
import yaml

import subprocess
import os
import socket
import glob
import sys


class DojoEventHandler(FileSystemEventHandler):
    """ Displays only the file that is being changed """

    def __init__(self, config, *args, **kwargs):
        super(DojoEventHandler, self).__init__(*args, **kwargs)
        handlers = config['handler']
        self.handlers = [ConsoleHandler(config['args'])]
        for h in handlers:
            handler = globals().get('{0}Handler'.format(h))
            if (handler and issubclass(handler, BaseHandler) and
                    handler is not BaseHandler and
                    handler is not ConsoleHandler):
                self.handlers.append(handler(config['args']))
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

    def __init__(self, args):
        self.args = args

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

    def __init__(self, args):
        super(MacNotifyHandler, self).__init__(args)
        try:
            from pync import Notifier
        except ImportError:
            puts(colored.red('Module pync not found, use: pip install pync'))
            sys.exit(1)
        self.notifier = Notifier

    def execute(self, event, return_code, proc):
        if return_code:
            message = 'Error!'
        else:
            message = "Success!"
        self.notifier.notify(message, title="EasyDojo")
        return super(MacNotifyHandler, self).execute(event, return_code, proc)


class ArduinoHandler(BaseHandler):
    """ Send a serial command to arduino with tests results """

    def __init__(self, args):
        super(MacNotifyHandler, self).__init__(args)
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


class UbuntuNotifyHandler(BaseHandler):
    """ Displays tests results on console and a Ubuntu Desktop notification """

    def __init__(self, args):
        super(UbuntuNotifyHandler, self).__init__(args)
        try:
            subprocess.check_call(['notify-send', '']) 
        except subprocess.CalledProcessError:
            pass
        except OSError:
            puts(colored.red('Package notify-send not installed. Please use: sudo apt-get install notify-osd'))
            sys.exit(1)
            
    def execute(self, event, return_code, proc):
        if return_code:
            message = 'Error!'
        else:
            message = 'Success!'

        subprocess.call(['notify-send', 'UbuntuNotify', message])

        return super(UbuntuNotifyHandler, self).execute(event, return_code, proc)


class SocketHandler(BaseHandler):
    """ Send a network command via socket with tests results.
            args:
                <host> - host of server
                <port> - port used on server
            example: easy_dojo watch --handler=Socket localhost 2020
    """

    def __init__(self, args):
        super(SocketHandler, self).__init__(args)
        if len(args) != 2:
            puts(colored.red('Args must be <host> <port>'))
            puts('Example:')
            with indent(4):
                puts('easy_dojo watch --handler=Socket localhost 2020')
            sys.exit(1)
        self.host = args[0]
        self.port = args[1]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, int(self.port)))
        except socket.error:
            puts(colored.red('Could not connect to server: {0}:{1}'.format(self.host, self.port)))
            sys.exit(1)
        except ValueError:
            puts(colored.red('Port must be a integer'))
            sys.exit(1)

    def execute(self, event, return_code, proc):
        if return_code:
            message = 'E'
        else:
            message = "S"
        try:
            self.sock.send(message)
        except socket.error:
            puts(colored.red('Unable to communicate with server: {0}:{1}'.format(self.host, self.port)))
        return super(SocketHandler, self).execute(event, return_code, proc)

    def __del__(self):
        if hasattr(self, 'sock'):
            self.sock.close()


class WebSocketHandler(BaseHandler):
    """ Send tests results via WebSocket.
            args:
                <url> - url to websocket server
            example: easy_dojo watch --handler=WebSocket ws://localhost:2020/ws
    """

    def __init__(self, args):
        super(WebSocketHandler, self).__init__(args)
        try:
            import websocket
        except ImportError:
            puts(colored.red('Module websocket-client not found, use: pip install websocket-client'))
            sys.exit(1)
        if len(args) != 1:
            puts(colored.red('Args must be <url>'))
            puts('Example:')
            with indent(4):
                puts('easy_dojo watch --handler=WebSocket ws://localhost:2020/ws')
            sys.exit(1)
        self.url = args[0]
        try:
            self.ws = websocket.create_connection(self.url)
        except (websocket.WebSocketException, socket.error):
            puts(colored.red('Could not connect to server: {0}'.format(self.url)))
            sys.exit(1)
        except ValueError:
            puts(colored.red('"{0}" is an invalid url'.format(self.url)))
            sys.exit(1)

    def execute(self, event, return_code, proc):
        import websocket
        if return_code:
            message = 'E'
        else:
            message = "S"
        try:
            self.ws.send(message)
        except (websocket.WebSocketException, socket.error):
            puts(colored.red('Unable to communicate with server: {0}'.format(self.url)))
        return super(WebSocketHandler, self).execute(event, return_code, proc)

    def __del__(self):
        if hasattr(self, 'ws'):
            self.ws.close()
