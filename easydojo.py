#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Easy Dojo

Usage:
  easydojo.py create <name>
  easydojo.py watch <name> [--handler=<handle>]
  easydojo.py list
  easydojo.py (-h | --help)
  easydojo.py --version

Options:
  --handler=<handle>     Handler used on watch command
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
from clint.textui import puts, colored, indent
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import os
import time
import unicodedata
import re
import sys
import subprocess


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', value.decode('utf-8')).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)


class DojoCommand(object):

    def __init__(self, command, config):
        self.config = config
        self.command = command
        self.name = config['name']

    def run(self):
        print('[{0}] Executing {1}...'.format(self.name, self.command))
        print self.config

    @staticmethod
    def make(arguments):
        config = {
            'name': arguments['<name>'],
            'handler': arguments['--handler'],
        }
        if arguments['create']:
            return CreateCommand('create', config)
        elif arguments['watch']:
            return WatchCommand('watch', config)
        elif arguments['list']:
            return ListHandlerCommand('list', config)


class CreateCommand(DojoCommand):

    def run(self):
        name = slugify(self.name)
        if os.path.exists(name):
            puts(colored.red('{name} exists existes'.format(name=name)))
            sys.exit(1)
        else:
            puts('Creating direcotry {name}...'.format(name=name))
            os.mkdir(name)
        puts('Creating main dojo file {name}/{name}.py'.format(name=name))
        open(os.path.join(name, '{name}.py'.format(name=name)), 'w').close()
        puts('Creating dojo test file {name}/test_{name}.py'.format(name=name))
        open(os.path.join(name, 'test_{name}.py'.format(name=name)), 'w').close()


class ListHandlerCommand(DojoCommand):
    def run(self):
        puts('List of all handlers:')
        for v in globals():
            if v.endswith('Handler') and issubclass(globals()[v], DojoEventHandler):
                with indent(4):
                    puts("{0} - {1}".format(v.replace('Handler', ''), globals()[v].__doc__))


class WatchCommand(DojoCommand):

    def run(self):
        path = slugify(self.name)
        handler = ConsoleHandler
        if self.config['handler']:
            try:
                handler = globals()['{handler}Handler'.format(handler=self.config['handler'])]
            except KeyError:
                puts(colored.red('Handler "{0}" not found!'.format(self.config['handler'])))
        puts('Running with {0} handler...'.format(handler.__name__.replace('Handler', '')))
        event_handler = handler(name=self.name)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


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


class EasyDojo(object):
    def __init__(self, arguments):
        self.command = DojoCommand.make(arguments)
        self.command.run()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='EasyDojo 0.1')
    dojo = EasyDojo(arguments)
