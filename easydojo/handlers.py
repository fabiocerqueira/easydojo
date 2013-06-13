from clint.textui import puts, colored, indent
from watchdog.events import FileSystemEventHandler
import yaml

import subprocess
import os


class DojoEventHandler(FileSystemEventHandler):
    """ Displays only the file that is being changed """

    def on_modified(self, event):
        valid = False
        if event.is_directory:
            return valid, 0, None
        filename = os.path.basename(event.src_path)
        config_file = os.path.join(os.getcwd(), '.easydojo.yaml')
        with open(config_file) as stream:
            config = yaml.load(stream)
        if filename not in config['files']:
            return valid, 0, None
        valid = True
        puts('Modified file {name}'.format(name=filename))
        puts('Running test runner:')
        puts(config['test_runner'])
        cmd = config['test_runner'].split()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return_code = proc.wait()
        return valid, return_code, proc


class ConsoleHandler(DojoEventHandler):
    """ Displays tests results on console, It's default. """

    def on_modified(self, event):
        valid, return_code, proc = super(ConsoleHandler, self).on_modified(event)
        if not valid:
            return valid, 0, None
        if return_code:
            quote = colored.red('||')
        else:
            quote = colored.green('||')
        with indent(4, quote=quote):
            puts(proc.stderr.read())
            puts(proc.stdout.read())
        return valid, return_code, proc


class MacNotifyHandler(ConsoleHandler):
    """ Displays tests results on console and a Mac Desktop notification """

    def on_modified(self, event):
        valid, return_code, proc = super(MacNotifyHandler, self).on_modified(event)
        if not valid:
            return valid, 0, None
        try:
            from pync import Notifier
        except ImportError:
            puts(colored.red('Module pync not found, use: pip install pync'))
            return valid, return_code, proc
        if return_code:
            message = 'Error!'
        else:
            message = "Success!"
        Notifier.notify(message, title="EasyDojo")
        return valid, return_code, proc
