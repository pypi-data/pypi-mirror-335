"""
Module used for defining the network class and it's functionality.
"""

import time
import datetime
from threading import Thread, Event
from queue import Queue
from os import makedirs
from os.path import dirname, exists
from typing import Union, List, Dict
from .Holder import PKIHolder
from .SocketUtils import start_socket_thread


class PKIHub:
    """
    The "infrastructure" of the network. Will be used to direct communications between holders.

    Attributes:
        outer_network (PKINetwork): The network object to access information and logging.
        message_queue (Queue): Queue to accept background holder logs.
        mirror_store (dict): The "mirror" of the environment hierarchy in literal name.
        loc_store (dict): The location of every holder in the environment.
        send_store (dict): Where to send information for each holder, split into sending "up" or "down" the PKI
            hierarchy.

    Methods:
        receive_log(holder_cat, holder_success, holder_act, holder_output, holder_name, holder_message) -> None:
            Takes a log from a holder and sends it to network logs.
    """
    def __init__(self, network, network_store: Dict[int, List[PKIHolder]]) -> None:
        # Basic attributes
        self.outer_network = network
        self.message_queue: Queue = Queue()

        # Create a mirror of network and location store
        self.mirror_store: dict = {}
        self.loc_store: dict = {}  # Sender = key, Receiver = value

        for level, holders in network_store.items():
            self.mirror_store[level] = []
            for holder in holders:
                # Add the address of the holder to the store
                self.mirror_store[level].append(holder.get_addr())

                # Add the location of the holder
                self.loc_store[holder.get_addr()] = (level, len(self.mirror_store[level]) - 1)

                # Set the hub for the holder
                holder.set_hub_conn(self)

        # Use mirror store to decide who to send things to.
        self.send_store: dict = {'up': {}, 'down': {}}
        for level in self.mirror_store.keys():
            # Skip first level
            if level == 1:
                continue

            prev_level: List[str] = self.mirror_store[level-1]
            prev_level_index: int = 0
            PREV_LEVEL_MAX: int = len(prev_level)

            for holder_addr in self.mirror_store[level]:
                # Record where the holder will send the message to
                self.send_store['up'][holder_addr] = prev_level[prev_level_index]

                # Record where the receiver can send the message back
                if prev_level[prev_level_index] in self.send_store['down'].keys():
                    self.send_store['down'][prev_level[prev_level_index]].append(holder_addr)
                else:
                    self.send_store['down'][prev_level[prev_level_index]] = [holder_addr]

                prev_level_index += 1
                if prev_level_index == PREV_LEVEL_MAX:
                    prev_level_index = 0

    def receive_log(self, holder_cat: str, holder_success: bool, holder_act: str, holder_output: str,
                    holder_name: str, holder_message: str) -> None:
        """
        Receives a log from a holder and saved it to network logs.
        """

        self.outer_network.log_event(
            holder_cat, holder_success, 'Holder', holder_act, holder_output, holder_name, holder_message
        )

    def forward_message(self) -> None:
        """
        Sends a message from one holder to another.
        """
        ...


class PKINetwork:
    """
    Represents a Public Key Infrastructure (PKI) network, including its configuration,
    hierarchy, and associated holders. This class provides functionality for managing
    the network, logging events, and filling configuration gaps.

    Attributes:
        network_name (str): Unique identifier for the network.
        log_save_fp (str): Where the logs will be saved to on storage drive.
        network_level_count (int): Total levels in the network hierarchy.
        network_count_by_level (List[int]): Number of holders at each level in the hierarchy.
        network_total_count (int): Total number of holders in the network.
        env_uid_hash (str): Unique identifier hash for the network environment.
        env_sig_hash (str): Signature hash used in the network.
        env_encrypt_alg (dict): Encryption algorithms supported by the network.
        env_revoc_probs (List[float]): Revocation probabilities by network level.
        env_cert_valid_durs (List[str]): Certificate validity durations by level.
        env_cache_durs (List[str]): Cache durations by network level.
        env_cooldown_durs (List[str]): Cooldown durations by network level.
        env_timeout_durs (List[str]): Timeout durations by network level.
        network (dict): Dictionary mapping network levels to their associated holders.
        network_log (List[str]): Log of events that occurred in the network.
        network_hub (PKIHub): Central hub for managing network communications.

    Methods:
        log_event(category, is_success, subject, act, output, origin, message) -> None:
            Prints the event that had happened and saves the information to network logs.
        save_logs() -> None:
            Saves the logs generated by the network to a CSV file.
        add_to_network(holder_name, holder_config, auto_config) -> bool:
            Adds a new holder to the network and returns a success status.
        get_network() -> List[PKIHolder]:
            Returns a flat list of all holders in network ordered by highest level.
        set_root_certificates() -> None:
            Sets up the certificate of root holders.
        start_network() -> None:
            Starts the PKI Simulation.
    """
    def __init__(self, name: str, auto_config: dict, manual_config: Union[dict, None] = None) -> None:
        # Unique identifier
        self.network_name: str = name

        # Runtime saving locations
        self.log_save_fp: str = auto_config['log_save_filepath']
        self.db_folder_path: str = auto_config['db_folder_path']

        # Network counts
        self.network_level_count: int = auto_config['level_count']
        self.network_count_by_level: List[int] = auto_config['count_by_level']
        self.network_total_count: int = 0

        # Environment variables
        self.env_uid_hash: str = auto_config['uid_hash']
        self.env_sig_hash: str = auto_config['sig_hash']
        self.env_encrypt_alg: dict = auto_config['encrypt_alg']
        self.env_revoc_probs: List[float] = auto_config['revoc_probs']
        self.env_cert_valid_durs: List[str] = auto_config['cert_valid_durs']
        self.env_cache_durs: List[str] = auto_config['cache_durs']
        self.env_cooldown_durs: List[str] = auto_config['cooldown_durs']
        self.env_timeout_durs: List[str] = auto_config['timeout_durs']
        self.env_runtime: str = auto_config['runtime']

        # Network hierarchy
        self.network: dict = {}
        for i in range(self.network_level_count):
            self.network[i+1] = []

        self.network_log: List[str] = ['ID, Timestamp, Category, Success, Subject, Act, Output, Origin, Message\n']

        # Log events that have already happened
        self.log_event(
            'Operations', True, 'Network', 'Initialization', 'Network',
            self.network_name, f'Network {self.network_name} created.'
        )
        self.log_event(
            'Operations', True, 'Network', 'Initialization', 'Variables',
            self.network_name, 'Environmental variables set.'
        )
        self.log_event(
            'Operations', True, 'Network', 'Initialization', 'Hierarchy',
            self.network_name, 'Empty network hierarchy created.'
        )
        self.log_event(
            'Operations', True, 'Network', 'Initialization', 'Log',
            self.network_name, 'Network log created and started.'
        )

        # Manual configuration
        if manual_config is not None:
            for holder_name, holder_config in manual_config.items():
                result: bool = self.add_to_network(holder_name, holder_config, auto_config)
                if result:
                    self.log_event(
                        'Operations', True, 'Network', 'Addition', holder_name,
                        self.network_name, f'Holder {holder_name} added to network.'
                    )
                    self.network_total_count += 1
                else:
                    self.log_event(
                        'Operations', False, 'Network', 'Omission', holder_name,
                        self.network_name, f'Invalid location configuration. {holder_name} was ignored.'
                    )

        # Filling in gaps
        auto_holder_count = 1
        for i in range(self.network_level_count):
            while len(self.network[i+1]) < self.network_count_by_level[i]:
                self.add_to_network(
                    f'holder_l{i+1}_c{auto_holder_count}',
                    {'location': {'level': i+1}},
                    auto_config
                )
                self.log_event(
                    'Operations', True, 'Network', 'Completion',
                    f'holder_l{i+1}_c{auto_holder_count}', self.network_name,
                    f'Gap found. Filler Holder #{auto_holder_count} at level {i+1} added to network.'
                )
                auto_holder_count += 1
                self.network_total_count += 1

        # Network hub
        self.network_hub = PKIHub(self, self.network)
        self.log_event(
            'Operations', True, 'Network', 'Initialization', 'Hub', self.network_name,
            'Network hub and connection information created.'
        )

    def log_event(self, category: str, is_success: bool, subject: str, act: str, output: str, origin: str,
                  message: str) -> None:
        """
        Takes a message, prints it, and saves its entry to network log with other elements.

        Categories that are used are:
            Operations - General Network activities
            PKI - Activities specific to PKI Practices.
            Communication - Activities specific to Communication.

        Args:
            category: str - The category of the message. One word.
            is_success: bool - The success status of the message.
            subject: str - The subject of the message. One word.
            act: str - The noun as an act the subject did. One word.
            output: str - The thing that resulted from the act. One word.
            origin: str - Who called the logging function. One word.
            message: str - String value to save.
        """

        id_num = len(self.network_log) - 1
        timestamp = datetime.datetime.now()
        entry = f'{id_num}, {timestamp}, {category}, {is_success}, {subject}, {act}, {output}, {origin}, {message}\n'

        print(message)
        self.network_log.append(entry)

    def save_logs(self) -> None:
        """
        Saves the logs to a csv file.
        """

        # Create one last log event
        self.log_event(
            'Operations', True, 'Network', 'Retention', 'CSV', self.network_name,
            f'Logs of network saved to {self.log_save_fp}.'
        )

        # Make a directory if it doesn't exist
        if not exists(dirname(self.log_save_fp)):
            makedirs(dirname(self.log_save_fp))

        # Save the log file
        with open(self.log_save_fp, 'w') as log_file:
            log_file.writelines(self.network_log)

    def add_to_network(self, holder_name: str, holder_config: dict, auto_config: dict) -> bool:
        """
        Takes a given holder name, holder configuration dictionary, and auto_config elements and creates a holder.
        Adds the holder to the growing network.

        Args:
            holder_name: str - The name of the manually created holder.
            holder_config: dict - The configuration settings of the holder.
            auto_config: dict - The configuration settings of the environment.

        Returns:
            bool - Success status on operation.
        """

        # Check if location is valid
        proper_keys: bool = all(
            isinstance(holder_config['location'][key], int) for key in holder_config['location'].keys()
        )
        enough_keys: bool = len(holder_config['location'].keys()) == 1
        if not proper_keys or not enough_keys:
            return False

        # Create holder
        holder: PKIHolder = PKIHolder(holder_name, holder_config, auto_config)

        # Add holder to network
        level: int = holder_config['location']['level']
        self.network[level].append(holder)

        return True

    def get_network(self) -> List[PKIHolder]:
        """
        Returns a flat list of all holders in the environment in order of level.

        Returns:
            List[PKIHolder]: A list of all holder objects.
        """

        flat_network: List[PKIHolder] = [holder for level in self.network.values() for holder in level]
        return flat_network

    def set_root_certificates(self) -> None:
        """
        Sets up the root certificates for the top level them passes them all to all holders.
        """

        # Generate self-signed certificates
        for root_holder in self.network[1]:
            new_cert = root_holder.gen_self_cert()

            if new_cert is not None:
                # Add root certificate to all root caches
                all_holders = self.get_network()
                for holder in all_holders:
                    holder.add_to_root_cache(root_holder.holder_info.url, new_cert)

    def start_network(self) -> None:
        """
        Starts the network until the user says otherwise.
        """
        print('\nNetwork started. To use the front-end environment, head to localhost:5000.\n')

        # TODO: Create A SQL database
        # TODO: Create GUI web app thread to start here
        # TODO: Create tests for the new module

        # Start the website
        website_stop_event = Event()

        # TODO: Add additional configuration setting for database saving
        website_socket_thread = Thread(
            name='pki_socket', target=start_socket_thread, args=(website_stop_event, self.db_folder_path,),
            daemon=True
        )
        website_socket_thread.start()

        # Create a time limit
        hours, minutes, seconds = map(int, self.env_runtime.split(":"))
        delta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        # delta = datetime.timedelta(minutes=2)
        end_time = datetime.datetime.now() + delta

        # Create additional threads
        main_holder_stop_event = Event()
        all_holders = self.get_network()
        all_holder_threads = [
            Thread(
                name=f'{holder.holder_name}_thread', target=holder.start_holder, args=(main_holder_stop_event,),
                daemon=True
            ) for holder in all_holders
        ]
        for thread in all_holder_threads:
            thread.start()

        # Start runtime loop
        while datetime.datetime.now() < end_time:
            time.sleep(1)

        website_stop_event.set()
        main_holder_stop_event.set()
