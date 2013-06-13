#-*- coding: utf-8 -*-
from clint.textui import puts, colored, indent
from watchdog.observers import Observer

from easydojo.utils import slugify
from easydojo import handlers, __version__

import os
import time
import sys


class DojoCommand(object):

    def __init__(self, command, config):
        self.config = config
        self.command = command
        self.name = config['name']
        self.dojo_file = os.path.join(os.getcwd(), '.easydojo.yaml')

    def run(self):
        print('Executing {0}...'.format(self.command))

    @staticmethod
    def make(arguments):
        config = {
            'name': arguments['<name>'],
            'handler': arguments['--handler'],
        }
        if arguments['init']:
            return InitCommand('init', config)
        elif arguments['watch']:
            return WatchCommand('watch', config)
        elif arguments['list']:
            return ListHandlerCommand('list', config)


class InitCommand(DojoCommand):

    def run(self):
        name = slugify(self.name)
        filename = "{0}.py".format(name)
        test_filename = "test_{0}.py".format(name)
        if os.listdir(os.getcwd()):
            puts(colored.red("This dir isn't empty"))
            sys.exit(1)
        if os.path.exists(self.dojo_file):
            puts(colored.red('EasyDojo already exists'))
            sys.exit(1)
        else:
            puts('Initialize {name}'.format(name=name))
            with open(self.dojo_file, 'w') as f:
                template = os.path.join(os.path.dirname(__file__), 'sample_easydojo.yaml')
                config_template = open(template).read()
                config = {
                    'version': __version__,
                    'filename': filename,
                    'test_filename': test_filename,
                    'test': 'test_{0}'.format(name),
                }
                f.write(config_template.format(**config))
            open(filename, 'w').close()
            open(test_filename, 'w').close()


class ListHandlerCommand(DojoCommand):
    def run(self):
        puts('List of all handlers:')
        for v in vars(handlers):
            if v.endswith('Handler') and issubclass(getattr(handlers, v), handlers.DojoEventHandler):
                with indent(4):
                    puts("{0} - {1}".format(v.replace('Handler', ''), getattr(handlers, v).__doc__))


class WatchCommand(DojoCommand):

    def run(self):
        if not os.path.exists(self.dojo_file):
            puts(colored.red("This path isn't an easydojo path"))
            puts("Use:")
            with indent(4):
                puts("easy_dojo init <name>")
            sys.exit(1)
        handler = handlers.ConsoleHandler
        if self.config['handler']:
            try:
                handler = getattr(handlers, '{handler}Handler'.format(handler=self.config['handler']))
            except KeyError:
                puts(colored.red('Handler "{0}" not found!'.format(self.config['handler'])))
        puts('Running with {0} handler...'.format(handler.__name__.replace('Handler', '')))
        event_handler = handler()
        observer = Observer()
        observer.schedule(event_handler, os.getcwd(), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
