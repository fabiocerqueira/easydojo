#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Easy Dojo

Usage:
  easydojo.py create <name> [--config=<config_file>]
  easydojo.py watch <name> [--config=<config_file>]
  easydojo.py (-h | --help)
  easydojo.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --config=<config_file>  Coding dojo configuration

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
        self.config_file = config['config_file']

    def run(self):
        print('[{0}] Executing {1}...'.format(self.name, self.command))
        print self.config

    @staticmethod
    def make(arguments):
        config = {
            'name': arguments['<name>'],
            "config_file": arguments['--config'],
        }
        if arguments['create']:
            return CreateCommand('create', config)
        elif arguments['watch']:
            return WatchCommand('watch', config)


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


class DojoEventHandler(FileSystemEventHandler):

    def __init__(self, name, *args, **kwargs):
        self.name = name
        super(FileSystemEventHandler, self).__init__(*args, **kwargs)

    def on_modified(self, event):
        name = slugify(self.name)
        filename = os.path.basename(event.src_path)
        if filename.endswith('%s.py' % name):
            puts('Modified file {name}'.format(name=filename))
            puts('Running tests...')
            cmd = ['python', '-m', 'unittest', 'discover', name, 'test_{name}.py'.format(name=name)]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return_code = proc.wait()
            with indent(2):
                puts(proc.stdout.read())
                puts(proc.stderr.read())
                if return_code:
                    puts(colored.red('Error test!'))
                else:
                    puts(colored.green('Ok test!'))


class WatchCommand(DojoCommand):

    def run(self):
        path = slugify(self.name)
        event_handler = DojoEventHandler(name=self.name)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


class EasyDojo(object):
    def __init__(self, arguments):
        self.command = DojoCommand.make(arguments)
        self.command.run()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='EasyDojo 0.1')
    dojo = EasyDojo(arguments)
