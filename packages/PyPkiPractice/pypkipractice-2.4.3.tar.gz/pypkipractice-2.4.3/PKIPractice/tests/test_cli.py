"""
Testing module for command line interface.
"""

import unittest
import subprocess
import random
import string
from typing import List

import sys
from os.path import abspath, dirname, join, basename, curdir
script_dir = dirname(abspath(__file__))
if script_dir in ['PKI_Practice', 'PKI Practice', 'app']:
    sys.path.append(abspath(script_dir))
elif script_dir == 'PKIPractice':
    sys.path.append(abspath(join(script_dir, '..')))
else:
    sys.path.append(abspath(join(script_dir, '../..')))


class TestCLI(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up the test environment.
        """
        current_dir = basename(abspath(curdir))
        if current_dir in ['PKI_Practice', 'PKI Practice', 'app']:
            self.dc_dir = './'
            self.pyfile = './PKIPractice/RunConfig.py'
        elif current_dir == 'PKIPractice':
            self.dc_dir = '../'
            self.pyfile = './RunConfig.py'
        elif current_dir == 'tests':
            self.dc_dir = '../../'
            self.pyfile = '../RunConfig.py'
        else:
            self.dc_dir = './'
            self.pyfile = './PKIPractice/RunConfig.py'

    def test_help(self) -> None:
        """
        Test the help flag.
        """
        result = subprocess.run(['python', self.pyfile, '-t', '-h'], capture_output=True)
        print(result)

        self.assertEqual(0, result.returncode, 'Test Help returned an invalid return code.')
        self.assertEqual(b'', result.stderr, 'Test Help returned an error message.')

        result = subprocess.run(['python', self.pyfile, '-t', '--help'], capture_output=True)
        print(result)

        self.assertEqual(0, result.returncode, 'Test Help returned an invalid return code.')
        self.assertEqual(b'', result.stderr, 'Test Help returned an error message.')

        result = subprocess.run(['python', self.pyfile, '-h'], capture_output=True)
        print(result)

        self.assertEqual(0, result.returncode, 'Help returned an invalid return code.')
        self.assertEqual(b'', result.stderr, 'Help returned an error message.')

        result = subprocess.run(['python', self.pyfile, '-h', '--help'], capture_output=True)
        print(result)

        self.assertEqual(0, result.returncode, 'Double Help returned an invalid return code.')
        self.assertEqual(b'', result.stderr, 'Double Help returned an error message.')

    def test_default(self) -> None:
        """
        Test the default flag.
        """
        result = subprocess.run(['python', self.pyfile, '-t', '-d'], capture_output=True)
        print(result)

        self.assertEqual(0, result.returncode, 'Test Default returned an invalid return code.')
        self.assertEqual(b'', result.stderr, 'Test Default returned an error message.')

        result = subprocess.run(['python', self.pyfile, '-t', '--default'], capture_output=True)
        print(result)

        self.assertEqual(0, result.returncode, 'Test Default returned an invalid return code.')
        self.assertEqual(b'', result.stderr, 'Test Default returned an error message.')

        result = subprocess.run(['python', self.pyfile, '-t', '-d', '--default'], capture_output=True)
        print(result)

        self.assertEqual(0, result.returncode, 'Test Double Default returned an invalid return code.')
        self.assertEqual(b'', result.stderr, 'Test Double Default returned an error message.')

    def test_args(self) -> None:
        """
        Test the arguments using files from Default_Configs folder.
        """
        arg_combos = [
            ['python', self.pyfile, '-t', '-a', f'{self.dc_dir}Default_Configs/default_auto.yaml'],
            ['python', self.pyfile, '-t', '-a', f'{self.dc_dir}Default_Configs/default_auto.json'],
            ['python', self.pyfile, '-t', '-a', f'{self.dc_dir}Default_Configs/default_auto.toml'],
            ['python', self.pyfile, '-t', '-a', f'{self.dc_dir}Default_Configs/default_auto.xml'],
            [
                'python',
                self.pyfile, '-t',
                '-a', f'{self.dc_dir}Default_Configs/default_auto.yaml',
                '-m', f'{self.dc_dir}Default_Configs/default_manual.yaml'
            ],
            [
                'python',
                self.pyfile, '-t',
                '-a', f'{self.dc_dir}Default_Configs/default_auto.json',
                '-m', f'{self.dc_dir}Default_Configs/default_manual.json'
            ],
            [
                'python',
                self.pyfile, '-t',
                '-a', f'{self.dc_dir}Default_Configs/default_auto.toml',
                '-m', f'{self.dc_dir}Default_Configs/default_manual.toml'
            ],
            [
                'python',
                self.pyfile, '-t',
                '-a', f'{self.dc_dir}Default_Configs/default_auto.xml',
                '-m', f'{self.dc_dir}Default_Configs/default_manual.xml'
            ]
        ]

        for args in arg_combos:
            result = subprocess.run(args, capture_output=True)
            print(result)

            self.assertEqual(
                0,
                result.returncode,
                f'Failed with args: {args}. {dirname(abspath(__file__))} Full file path: {abspath(self.pyfile)}'
            )
            self.assertEqual(
                b'',
                result.stderr,
                f'Failed with args: {args}. {dirname(abspath(__file__))} Full file path: {abspath(self.pyfile)}'
            )

    def test_fail(self) -> None:
        """
        Fuzz Test to check argument error detection.
        """
        def generate_random_string(min_length: int = 1, max_length: int = 20) -> str:
            """Generate a random string of random length."""
            length = random.randint(min_length, max_length)  # Random length between min_length and max_length
            return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))

        def generate_random_string_list(
                min_items: int = 1, max_items: int = 3, min_length: int = 1, max_length: int = 20) -> List[str]:
            """Generate a list of random strings with random length and random number of items."""
            num_items = random.randint(min_items, max_items)  # Random number of items in the list
            return [generate_random_string(min_length, max_length) for _ in range(num_items)]

        # Fuzzing loop
        for i in range(100):
            args = ['python', self.pyfile] + generate_random_string_list()
            result = subprocess.run(args, capture_output=True)
            print(result)

            safely_quit = result.returncode == 0
            detected_ambiguous = 'ambiguous' in result.stderr.decode('utf-8')
            detected_error = 'Exception' in result.stdout.decode('utf-8') or 'Warning' in result.stdout.decode('utf-8')
            detected_help_normal = any(help_option in args for help_option in ('-h', '--help'))
            detected_help_misc = any(option[0] == '-' and 'h' in option for option in args)

            if not detected_help_normal and not detected_help_misc:
                self.assertTrue(
                    safely_quit or detected_ambiguous,
                    f'Failed with args: {args}. Full file path: {abspath(self.pyfile)}'
                )
                self.assertTrue(detected_error, f'Failed with args: {args}. Full file path: {abspath(self.pyfile)}')

    def test_warning(self) -> None:
        """
        Test to check if warning raised about too many argument.
        """
        args = [
            'python',
            self.pyfile, '-t',
            '-a', f'{self.dc_dir}Default_Configs/default_auto.json',
            '-m', f'{self.dc_dir}Default_Configs/default_manual.json',
            'one too many arguments'
        ]
        result = subprocess.run(args, capture_output=True)
        print(result)

        safely_quit = result.returncode == 0
        detected_too_many_args = 'Warning' in result.stdout.decode('utf-8')

        self.assertTrue(safely_quit, f'Failed with args: {args}. Full file path: {abspath(self.pyfile)}')
        self.assertTrue(
            detected_too_many_args, f'Failed with args: {args}. Full file path: {abspath(self.pyfile)}'
        )
