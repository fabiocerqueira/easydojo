from clint.textui import puts, colored, indent
from watchdog.events import FileSystemEventHandler

from easydojo.utils import slugify

import subprocess
import os


class DojoEventHandler(FileSystemEventHandler):
    """ Displays only the file that is being changed """

    def __init__(self, name, *args, **kwargs):
        self.name = name
        super(FileSystemEventHandler, self).__init__(*args, **kwargs)

    def on_modified(self, event):
        name = slugify(self.name)
        filename = os.path.basename(event.src_path)
        valid = False
        if filename.endswith('%s.py' % name):
            valid = True
            puts('Modified file {name}'.format(name=filename))
            puts('Running tests...')
            cmd = ['python', '-m', 'unittest', 'discover', name, 'test_{name}.py'.format(name=name)]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return_code = proc.wait()
            return valid, return_code, proc
        else:
            return valid, 0, None


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
            Notifier.notify('Error!', title="EasyDojo[{name}]".format(name=self.name))
        else:
            Notifier.notify('Success!', title="EasyDojo[{name}]".format(name=self.name))
        return valid, return_code, proc
