"""
Module for testing the holder class.
"""

import unittest
from time import sleep
from random import choice, randint
import threading
from argparse import ArgumentParser

import sys
from os.path import abspath, dirname, join
script_dir = dirname(abspath(__file__))
if script_dir in ['PKI_Practice', 'PKI Practice', 'app']:
    sys.path.append(abspath(script_dir))
elif script_dir == 'PKIPractice':
    sys.path.append(abspath(join(script_dir, '..')))
else:
    sys.path.append(abspath(join(script_dir, '../..')))

from PKIPractice.Utilities.CLIUtils import ingest_config
from PKIPractice.Simulation.Network import PKINetwork
from PKIPractice.Simulation.Holder import PKIHolder


class TestHolder(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the parameters for testing.
        """
        parser: ArgumentParser = ArgumentParser(
            prog='run-pki-practice',
            usage='run-pki-practice [Options]',
            description=('run-pki-practice is the command line interface for the PKI practice program.\n'
                         'For more information see the README.\n')
        )
        parser.add_argument(
            '-a', '--auto', type=str, required=False, help='The filepath of the auto configuration file.',
            dest='auto_config_fp'
        )
        parser.add_argument(
            '-m', '--manual', type=str, required=False, help='The filepath of the manual configuration file.',
            dest='manual_config_fp'
        )
        parser.add_argument(
            '-t', '--test', action='store_true', default=False, required=False,
            help=('Run the program in test mode. This mode is mainly used by testing modules, but it stops the program '
                  'before the PKI network is started to save time.'), dest='test_mode_on'
        )
        parser.add_argument(
            '-d', '--default', action='store_true', default=False, required=False,
            help='Run the program in default mode. This mode overrides the need for configuration files.',
            dest='default_mode_on'
        )
        args, _ = parser.parse_known_args(['--default'])
        self.env_auto_settings, _ = ingest_config(args)
        self.auto_network = PKINetwork('Test_Net', self.env_auto_settings)

    def test_root_cert_generation(self) -> None:
        """
        Tests the ability for roots and non roots to create certificates.
        """
        random_root_ca: PKIHolder = choice(self.auto_network.network[1])
        random_inter_ca: PKIHolder = choice(self.auto_network.network[
            randint(2, self.auto_network.network_level_count - 1)
        ])
        random_non_ca: PKIHolder = choice(self.auto_network.network[self.auto_network.network_level_count])

        self.assertIsNotNone(
            random_root_ca.gen_self_cert(),
            'The root holder was unable to generate a self certificate.'
        )
        self.assertIsNone(
            random_inter_ca.gen_self_cert(),
            'The intermediate holder was able to generate a self certificate.'
        )
        self.assertIsNone(
            random_non_ca.gen_self_cert(),
            'The non root holder was able to generate a self certificate.'
        )

    def test_service_creation(self) -> None:
        """
        Tests what services are created for CAs and Non-CAs.
        """
        # Test Random CA
        random_inter_ca: PKIHolder = choice(self.auto_network.network[
            randint(1, self.auto_network.network_level_count - 1)
        ])
        ca_event: threading.Event = threading.Event()

        test_thread = threading.Thread(target=random_inter_ca.start_holder, args=(ca_event,), daemon=True)
        test_thread.start()
        sleep(3)
        ca_event.set()

        thread_names = [thread.name for thread in threading.enumerate()]
        self.assertTrue(
            any(f'{random_inter_ca.holder_name}_cert_thread' in thread_name for thread_name in thread_names),
            'The certificate management thread was not created for CA.'
        )
        self.assertTrue(
            any(f'{random_inter_ca.holder_name}_ca_rsp_thread' in thread_name for thread_name in thread_names),
            'The CA response thread was not created for CA.'
        )
        self.assertTrue(
            any(f'{random_inter_ca.holder_name}_ca_crl_thread' in thread_name for thread_name in thread_names),
            'The CA revocation management thread was not created for CA.'
        )
        self.assertFalse(
            any(f'{random_inter_ca.holder_name}_msg_thread' in thread_name for thread_name in thread_names),
            'The regular messaging thread should not have been created for CA.'
        )
        is_holder_thread = (random_inter_ca.holder_name in thread_name for thread_name in thread_names)
        self.assertEqual(3, sum(is_holder_thread), 'There were not exactly three services started for CA.')

        # Test Random Non-CA
        random_non_ca: PKIHolder = choice(self.auto_network.network[self.auto_network.network_level_count])
        non_ca_event: threading.Event = threading.Event()

        test_thread = threading.Thread(target=random_non_ca.start_holder, args=(non_ca_event,), daemon=True)
        test_thread.start()
        sleep(3)
        non_ca_event.set()

        thread_names = [thread.name for thread in threading.enumerate()]
        self.assertTrue(
            any(f'{random_non_ca.holder_name}_cert_thread' in thread_name for thread_name in thread_names),
            'The certificate management thread was not created for CA.'
        )
        self.assertFalse(
            any(f'{random_non_ca.holder_name}_ca_rsp_thread' in thread_name for thread_name in thread_names),
            'The CA response thread should not have been created for non-CA.'
        )
        self.assertFalse(
            any(f'{random_non_ca.holder_name}_ca_crl_thread' in thread_name for thread_name in thread_names),
            'The CA revocation management thread should not have been created for non-CA.'
        )
        self.assertTrue(
            any(f'{random_non_ca.holder_name}_msg_thread' in thread_name for thread_name in thread_names),
            'The regular messaging thread was not created for non-CA.'
        )
        is_holder_thread = (random_non_ca.holder_name in thread_name for thread_name in thread_names)
        self.assertEqual(2, sum(is_holder_thread), 'There were not exactly two services started for non-CA.')
