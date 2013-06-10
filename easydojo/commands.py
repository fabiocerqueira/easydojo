#-*- coding: utf-8 -*-
from clint.textui import puts, colored, indent
from watchdog.observers import Observer

from easydojo.utils import slugify
from easydojo import handlers

import os
import time
import sys


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
        for v in vars(handlers):
            if v.endswith('Handler') and issubclass(getattr(handlers, v), handlers.DojoEventHandler):
                with indent(4):
                    puts("{0} - {1}".format(v.replace('Handler', ''), getattr(handlers, v).__doc__))


class WatchCommand(DojoCommand):

    def run(self):
        path = slugify(self.name)
        handler = handlers.ConsoleHandler
        if self.config['handler']:
            try:
                handler = getattr(handlers, '{handler}Handler'.format(handler=self.config['handler']))
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
