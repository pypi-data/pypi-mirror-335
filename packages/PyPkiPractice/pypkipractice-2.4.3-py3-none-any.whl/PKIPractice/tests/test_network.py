"""
Module for testing the network class.
"""

import unittest
import time
import tempfile
from threading import enumerate
from datetime import datetime
from typing import List
from argparse import ArgumentParser

import sys
from os.path import abspath, dirname, join, exists
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


class TestNetwork(unittest.TestCase):
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
        self.env_auto_settings, self.env_manual_settings = ingest_config(args)

    def test_network_creation(self) -> None:
        """
        Tests the ability to create a whole network object.
        """

        pki_network: PKINetwork = PKINetwork('Test_Net', self.env_auto_settings)
        self.assertIsNotNone(pki_network, 'Something went wrong when generating autoconfiguration.')

        pki_network: PKINetwork = PKINetwork('Test_Net', self.env_auto_settings, self.env_manual_settings)
        self.assertIsNotNone(pki_network, 'Something went wrong when generating auto and manual configuration.')

    def test_holders(self) -> None:
        """
        Tests the creation and organization of holders.
        """

        auto_network: PKINetwork = PKINetwork('Test_Net', self.env_auto_settings)
        manual_network: PKINetwork = PKINetwork('Test_Net', self.env_auto_settings, self.env_manual_settings)

        for pki_network in [auto_network, manual_network]:
            all_holders: List[PKIHolder] = pki_network.get_network()

            # Assert that all holders were created
            self.assertEqual(
                sum(pki_network.network_count_by_level),
                len(all_holders),
                'All required holders were not created (by level count).'
            )
            self.assertEqual(
                len(all_holders),
                pki_network.network_total_count,
                'All required holders were not created (by total count).'
            )

            # Assert the right amount of holders were created per level
            for i in range(pki_network.network_level_count):
                self.assertEqual(
                    pki_network.network_count_by_level[i],
                    len(pki_network.network[i+1]),
                    f'All required holders for level {i+1} were not created.'
                )

            # Assert the top level of holders are all root CAs
            for holder in pki_network.network[1]:
                self.assertTrue(
                    holder.holder_type_info.ca_status == 'root_auth',
                    'All first level holders are not root CAs.'
                )

            # Assert all levels but the first and last are intermediate CAs
            for i in range(1, pki_network.network_level_count - 1):
                for holder in pki_network.network[i+1]:
                    self.assertTrue(
                        holder.holder_type_info.ca_status == 'inter_auth',
                        f'All level {i+1} holders are not intermediary CAs.'
                    )

            # Assert the bottom level of holders are not CAs
            for holder in pki_network.network[pki_network.network_level_count]:
                self.assertTrue(
                    holder.holder_type_info.ca_status == 'not_auth',
                    'All last level holders are not regular holders.'
                )

    def test_thread_ending(self) -> None:
        """
        Tests the ability to end a thread in a short amount of time.
        """
        # Adjust runtime length for purpose of test
        self.env_auto_settings["runtime"] = "00:00:05"
        auto_network: PKINetwork = PKINetwork('Test_Net', self.env_auto_settings)
        auto_network.set_root_certificates()

        # Let the network run for a few seconds
        auto_network.start_network()

        # Get the thread count after giving some time for things to spin down
        time.sleep(2)
        thread_names = [thread.name for thread in enumerate()]
        print(thread_names)

        self.assertTrue(
            all((f'{holder.holder_name}' not in thread_names for holder in auto_network.get_network())),
            'The daemon threads did not end once the network signalled a stoppage.'
        )

    def test_log_output(self) -> None:
        """
        Tests the ability to create a proper log file.
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            # Set filepath
            new_fp: str = join(temp_dir, self.env_auto_settings["log_save_filepath"])
            self.env_auto_settings["log_save_filepath"] = new_fp

            # Create the network
            pki_network: PKINetwork = PKINetwork('Test Net With Space', self.env_auto_settings)
            pki_network.save_logs()

            # Run tests on temporary file
            self.assertTrue(exists(new_fp), 'The test file was not created properly.')

            with open(new_fp, 'r') as f:
                output: List[str] = f.readlines()

                # Compact tests
                # Header row
                self.assertEqual(
                    output[0],
                    'ID, Timestamp, Category, Success, Subject, Act, Output, Origin, Message\n',
                    'The expected header row was not found.'
                )

                # New lines
                self.assertTrue(all(line[-1:] == '\n' for line in output), 'All lines do not end with a new line.')

                # Right amount of commas
                self.assertTrue(
                    all(line.count(',') == 8 for line in output),
                    'All lines do not have the right amonut of commas.'
                )

                # Detailed tests
                for line in output:
                    row: List[str] = line.split(',')

                    if row[0] == 'ID':
                        continue

                    test_successful: bool = True
                    try:
                        # Convertable ID
                        self.assertIsInstance(
                            int(row[0]), int,
                            f'The first value in row {row} could not be read as an integer.'
                        )

                        # Proper timestamp
                        self.assertIsInstance(
                            datetime.strptime(row[1], ' %Y-%m-%d %H:%M:%S.%f'),
                            datetime,
                            f'The timestamp in row {row} could not be read as a proper datetime object.'
                        )

                        # No spaces in one-word items
                        self.assertTrue(
                            all(" " not in item.strip() for item in row[2:7]),
                            f'There were spaces found in one-word columns for row {row}'
                        )
                    except (TypeError, ValueError):
                        test_successful = False

                    # Everything passed without an exception
                    self.assertTrue(test_successful, f'Item-wise row tests did not pass safely for row {row}')


if __name__ == "__main__":
    unittest.main()
