#-*- coding: utf-8 -*-
from clint.textui import puts, colored, indent
from watchdog.observers import Observer

from easydojo import __version__, handlers
from easydojo.utils import slugify
from easydojo.panel import server

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
        if arguments['--handlers']:
            handler_list = [h.strip() for h in arguments['--handlers'].split(',')]
        else:
            handler_list = []
        config = {
            'name': arguments['<name>'],
            'args': arguments['<args>'],
            'handler': handler_list,
            'port': arguments['<port>'],
        }
        if arguments['init']:
            return InitCommand('init', config)
        elif arguments['watch']:
            return WatchCommand('watch', config)
        elif arguments['panel']:
            return PanelCommand('panel', config)
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


class PanelCommand(DojoCommand):
    def run(self):
        try:
            if self.config['port']:
                server.main(int(self.config['port']))
            else:
                server.main()
        except ValueError:
            puts(colored.red('Port must be a integer'))
            sys.exit(1)


class ListHandlerCommand(DojoCommand):
    def run(self):
        puts('List of all handlers:')
        for v in vars(handlers):
            if (v.endswith('Handler') and
                    getattr(handlers, v) is not handlers.BaseHandler and
                    getattr(handlers, v) is not handlers.ConsoleHandler and
                    issubclass(getattr(handlers, v), handlers.BaseHandler)):
                with indent(4):
                    puts("* {0} - {1}\n".format(v.replace('Handler', ''), getattr(handlers, v).__doc__))


class WatchCommand(DojoCommand):

    def run(self):
        if not os.path.exists(self.dojo_file):
            puts(colored.red("This path isn't an easydojo path"))
            puts("Use:")
            with indent(4):
                puts("easy_dojo init <name>")
            sys.exit(1)
        event_handler = handlers.DojoEventHandler(self.config)
        observer = Observer()
        observer.schedule(event_handler, os.getcwd(), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
