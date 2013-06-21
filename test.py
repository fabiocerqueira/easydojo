import unittest
import sys
import os
import shutil
from StringIO import StringIO


class InitCommandTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.output = StringIO()
        cls.saved_stdout = sys.stdout
        sys.stdout = cls.output
        cls.sys_exit = sys.exit
        sys.exit = lambda x: x

    def setUp(self):
        InitCommandTest.output.truncate(0)

    def test_init_with_name_empty_dir(self):
        from easydojo.commands import DojoCommand
        path = 'example42'
        os.mkdir(path)
        os.chdir(path)
        arguments = {
            '<name>': 'example42',
            'init': True,
            '--handlers': None,
            '<args>': None,
            '<port>': None,
        }
        cmd = DojoCommand.make(arguments)
        cmd.run()
        self.assertTrue(os.path.exists('.easydojo.yaml'))
        self.assertTrue(os.path.exists('example42.py'))
        self.assertTrue(os.path.exists('test_example42.py'))
        self.assertIn("Initialize example42", InitCommandTest.output.getvalue())
        os.chdir('..')
        shutil.rmtree(path)

    def test_init_with_name_already_easydojo_dir(self):
        from easydojo.commands import DojoCommand
        path = 'example42'
        os.mkdir(path)
        os.chdir(path)
        arguments = {
            '<name>': 'example42',
            'init': True,
            '--handlers': None,
            '<args>': None,
            '<port>': None,
        }
        cmd = DojoCommand.make(arguments)
        cmd.run()
        self.assertIn("Initialize example42", InitCommandTest.output.getvalue())
        cmd.run()
        self.assertIn("EasyDojo already exists", InitCommandTest.output.getvalue())
        os.chdir('..')
        shutil.rmtree(path)

    def test_init_with_name_not_empty_dir(self):
        from easydojo.commands import DojoCommand
        arguments = {
            '<name>': 'example42',
            'init': True,
            '--handlers': None,
            '<args>': None,
            '<port>': None,
        }
        cmd = DojoCommand.make(arguments)
        cmd.run()
        self.assertIn("This dir isn't empty", InitCommandTest.output.getvalue())

    @classmethod
    def tearDownClass(cls):
        cls.output.close()
        sys.stdout = cls.saved_stdout
        sys.exit = cls.sys_exit


if __name__ == '__main__':
    unittest.main()
