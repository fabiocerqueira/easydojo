import unittest
import sys
import os
import shutil
from StringIO import StringIO

sys.exit = lambda x: x
OUTPUT = StringIO()
sys.stdout = OUTPUT


class CommandTest(unittest.TestCase):

    def setUp(self):
        OUTPUT.truncate(0)


class InitCommandTest(CommandTest):

    def setUp(self):
        super(InitCommandTest, self).setUp()
        self.arguments = {
            '--handlers': None,
            '--help': False,
            '--version': False,
            '<args>': [],
            '<name>': 'example42',
            '<port>': None,
            'init': True,
            'list': False,
            'panel': False,
            'watch': False
        }

    def test_init_with_name_empty_dir(self):
        from easydojo.commands import DojoCommand
        path = 'example42'
        os.mkdir(path)
        os.chdir(path)
        cmd = DojoCommand.make(self.arguments)
        cmd.run()
        self.assertTrue(os.path.exists('.easydojo.yaml'))
        self.assertTrue(os.path.exists('example42.py'))
        self.assertTrue(os.path.exists('test_example42.py'))
        self.assertIn("Initialize example42", OUTPUT.getvalue())
        os.chdir('..')
        shutil.rmtree(path)

    def test_init_with_name_already_easydojo_dir(self):
        from easydojo.commands import DojoCommand
        path = 'example42'
        os.mkdir(path)
        os.chdir(path)
        cmd = DojoCommand.make(self.arguments)
        cmd.run()
        self.assertIn("Initialize example42", OUTPUT.getvalue())
        cmd.run()
        self.assertIn("EasyDojo already exists", OUTPUT.getvalue())
        os.chdir('..')
        shutil.rmtree(path)

    def test_init_with_name_not_empty_dir(self):
        from easydojo.commands import DojoCommand
        cmd = DojoCommand.make(self.arguments)
        cmd.run()
        self.assertIn("This dir isn't empty", OUTPUT.getvalue())


class ListCommandTest(CommandTest):

    def setUp(self):
        super(ListCommandTest, self).setUp()
        self.arguments = {
            '--handlers': None,
            '--help': False,
            '--version': False,
            '<args>': [],
            '<name>': None,
            '<port>': None,
            'init': False,
            'list': True,
            'panel': False,
            'watch': False
        }

    def test_list(self):
        from easydojo.commands import DojoCommand
        cmd = DojoCommand.make(self.arguments)
        cmd.run()
        self.assertIn('List of all handlers:', OUTPUT.getvalue())


if __name__ == '__main__':
    unittest.main()
