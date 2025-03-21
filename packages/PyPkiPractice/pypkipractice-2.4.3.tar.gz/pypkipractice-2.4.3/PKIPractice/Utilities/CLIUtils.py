"""
Module containing all utilities relevant for interacting with a command line interface.
"""

from typing import Union
from argparse import ArgumentParser, Namespace
from .IngestUtils import *

import sys
from os.path import abspath, dirname, join
script_dir = dirname(abspath(__file__))
if script_dir in ['PKI_Practice', 'PKI Practice', 'app']:
    sys.path.append(abspath(script_dir))
elif script_dir == 'PKIPractice':
    sys.path.append(abspath(join(script_dir, '..')))
else:
    sys.path.append(abspath(join(script_dir, '../..')))

from PKIPractice.Simulation.Network import PKINetwork


def get_default_auto() -> dict:
    """
    Retrieve the default autoconfiguration

    Returns:
        dict: The default autoconfiguration
    """
    auto_config: dict = {
        "level_count": 4,
        "count_by_level": [1, 2, 4, 8],
        "uid_hash": "sha256",
        "sig_hash": "sha256",
        "encrypt_alg": {
            "alg": "rsa",
            "params": {
                "pub_exp": 65537,
                "key_size": 2048
            }
        },
        "revoc_probs": [0.0, 0.0001, 0.001, 0.01],
        "cert_valid_durs": ["none", "00:15:00", "00:10:00", "00:05:00"],
        "cache_durs": ["none", "11:00", "06:00", "01:00"],
        "cooldown_durs": ["5", "5", "5", "5"],
        "timeout_durs": ["20", "20", "20", "20"],
        "runtime": "00:30:00",
        "log_save_filepath": "output/saved_network_logs_default.csv",
        "db_folder_path": "output/database"
    }

    return auto_config


def get_default_manual() -> dict:
    """
    Retrieve the default manual configuration

    Returns:
        dict: The default manual configuration
    """
    manual_config: dict = {
        "default_root_ca": {
            "location": {
                "level": 1
            },
            "env_overrides": {
                "uid_hash": "sha3_512",
                "sig_hash": "sha3_512",
                "encrypt_alg": {
                    "alg": "ecc",
                    "params": {
                        "curve": "secp256r1"
                    }
                },
                "revoc_prob": 0.0,
                "cert_valid_dur": "none",
                "cache_dur": "none",
                "cooldown_dur": "10",
                "timeout_dur": "40"
            },
            "holder_type_info": {
                "hardware_type": "endpoint",
                "hardware_subtype": "server",
                "hardware_brand": "dell",
                "os_category": "microsoft",
                "os_subcategory": "windows_server",
                "os_dist": "windows_server_2019",
                "os_subdist": "standard",
                "account_type": "admin",
                "account_subtype": "domain_admin",
                "ca_status": "root_auth"
            },
            "holder_info": {
                "common_name": "Root Enterprises Root CA",
                "country": "US",
                "state": "CA",
                "locality": "San Francisco",
                "org": "Root Enterprises",
                "org_unit": "Certificates",
                "email": "root_ca_team@root_enterprises.com",
                "url": "root_enterprises.com/root_ca"
            }
        },
        "second_lvl_ca_one": {
            "location": {
                "level": 2
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512",
                "encrypt_alg": {
                    "alg": "ecc",
                    "params": {
                        "curve": "secp256r1"
                    }
                }
            },
            "holder_type_info": {
                "os_category": "unix",
                "os_subcategory": "linux",
                "os_dist": "ubuntu_server"
            }
        },
        "second_lvl_ca_two": {
            "location": {
                "level": 2
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512",
                "encrypt_alg": {
                    "alg": "ecc",
                    "params": {
                        "curve": "secp256r1"
                    }
                }
            },
            "holder_type_info": {
                "os_category": "unix",
                "os_subcategory": "linux",
                "os_dist": "ubuntu_server"
            }
        },
        "third_lvl_ca_one": {
            "location": {
                "level": 3
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512"
            },
            "holder_info": {
                "common_name": "Cert Incorporated South America CA",
                "country": "PE",
                "state": "Lima",
                "locality": "Ventanilla",
                "org": "Cert Incorporated",
                "org_unit": "South American Certificates",
                "email": "certs_sa@cert_incorporated.com",
                "url": "cert_incorporated.com/peru/intermediate_ca"
            }
        },
        "third_lvl_ca_two": {
            "location": {
                "level": 3
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512"
            },
            "holder_info": {
                "common_name": "CloudCert Inc West Africa CA",
                "country": "NG",
                "state": "Oyo",
                "locality": "Ibadan",
                "org": "CloudCert Inc",
                "org_unit": "West African Certificates",
                "email": "certs_africa@cloudcert.com",
                "url": "cloudcert.com/nigeria/intermediate_ca"
            }
        },
        "third_lvl_ca_three": {
            "location": {
                "level": 3
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512"
            },
            "holder_info": {
                "common_name": "EuroPass International Norway CA",
                "country": "NO",
                "state": "Bergen",
                "locality": "Kokstad",
                "org": "EuroPass International",
                "org_unit": "Western European Certificates",
                "email": "certs_europe@europass.com",
                "url": "europass.com/norway_intermediate_ca"
            }
        },
        "third_lvl_ca_four": {
            "location": {
                "level": 3
            },
            "env_overrides": {
                "uid_hash": "sha512",
                "sig_hash": "sha512"
            },
            "holder_info": {
                "common_name": "Lone Star Networking Houston CA",
                "country": "US",
                "state": "Texas",
                "locality": "Houston",
                "org": "Lone Star Networking",
                "org_unit": "North American Certificates",
                "email": "lone_star_certs@lonestarnet.com",
                "url": "lonestarnet.com/us/houston/intermediate_ca"
            }
        },
        "fourth_level_one": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "network",
                "hardware_subtype": "access_point",
                "hardware_brand": "cisco",
                "os_category": "routing",
                "os_subcategory": "openwrt",
                "os_dist": "openwrt",
                "os_subdist": "openwrt",
                "account_type": "admin",
                "account_subtype": "network_admin"
            }
        },
        "fourth_level_two": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "endpoint",
                "hardware_subtype": "laptop",
                "hardware_brand": "asus",
                "os_category": "microsoft",
                "os_subcategory": "windows",
                "os_dist": "windows_10",
                "os_subdist": "home",
                "account_type": "user",
                "account_subtype": "personal"
            }
        },
        "fourth_level_three": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "peripheral",
                "hardware_subtype": "smart_card"
            }
        },
        "fourth_level_four": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "endpoint",
                "hardware_subtype": "phone",
                "account_type": "user"
            }
        },
        "fourth_level_five": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "appliance",
                "hardware_subtype": "utm",
                "hardware_brand": "barracuda"
            }
        },
        "fourth_level_six": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "endpoint",
                "hardware_subtype": "desktop",
                "os_category": "unix",
                "os_subcategory": "solaris",
                "account_subtype": "cloud_admin"
            }
        },
        "fourth_level_seven": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "hardware_type": "endpoint",
                "hardware_subtype": "iot",
                "hardware_brand": "arduino",
                "os_category": "unix",
                "os_subcategory": "linux",
                "os_dist": "alpine",
                "os_subdist": "alpine",
                "account_type": "user",
                "account_subtype": "guest"
            }
        },
        "fourth_level_eight": {
            "location": {
                "level": 4
            },
            "holder_type_info": {
                "os_subcategory": "mac_os_x"
            }
        }
    }

    return manual_config


def ingest_config(args: Namespace) -> Union[tuple, None]:
    """
    Starts the program using the command-line arguments.

    Args:
        args (Namespace): A parsed collection of command-line arguments.
    """

    # Check if a yaml file is passed on an interpreter before Python 3.10
    if sys.version_info[1] < 10 and args.auto_config_fp is not None:
        assert '.yaml' not in args.auto_config_fp, (
            """
Invalid configuration filepath provided.
    Yaml files do not have support for Python versions before 3.10.
    Please use a different configuration format (JSON, XML, TOML).  
            """
        )
    if sys.version_info[1] < 10 and args.manual_config_fp is not None:
        assert '.yaml' not in args.manual_config_fp, (
            """
Invalid configuration filepath provided.
    Yaml files do not have support for Python versions before 3.10.
    Please use a different configuration format (JSON, XML, TOML).  
            """
        )

    # Check if there is a proper argument for the auto generation
    if not args.default_mode_on:
        assert 'auto' in args.auto_config_fp, (
            """
Invalid configuration filepath provided.
Please provide a proper auto configuration file by passing the filepath of your file as an 
    command-line argument.

Examples:
    python RunConfig.py -a Default_Configs/default_auto.yaml
    run-pki-practice --auto Default_Configs/default_auto.yaml
            """
        )

    # Check if there is a proper argument for the manual settings or if it's just one argument
    only_auto_or_default: bool = args.manual_config_fp is None or args.default_mode_on
    if only_auto_or_default:
        manual_exists: bool = True
    else:
        manual_exists: bool = 'manual' in args.manual_config_fp
    assert manual_exists is True, (
        """
Invalid configuration filepath provided. Please provide a proper manual configuration file by passing the 
    filepath of your file as a command-line argument.
    
Examples: 
    python RunConfig.py -a Default_Configs/default_auto.yaml -m Default_Configs/default_manual.yaml
    run-pki-practice --auto Default_Configs/default_auto.yaml --manual Default_Configs/default_manual.yaml
        """
    )

    # Pass auto argument to ingestion utilities
    if args.default_mode_on:
        env_auto_settings: Union[dict, None] = get_default_auto()
        assert validate_settings_auto(env_auto_settings) is True, (
            """
Ingested default mode autoconfiguration settings were not found to be valid.
    This is an issue with the default settings. Please report an issue at 
    https://github.com/laoluadewoye/PKI_Practice_Python
            """
        )
    else:
        env_auto_settings: Union[dict, None] = parse_config_auto(args.auto_config_fp)

    # Pass manual argument to ingestion utilities
    if args.default_mode_on:
        env_manual_settings: Union[dict, None] = get_default_manual()
        env_manual_settings = search_for_typecast_manual(env_manual_settings)
        assert env_manual_settings is not None, (
            """
Ingested default mode manual configuration settings were not able to be adjusted due to unparsable 
    configuration params.
    This is an issue with the default settings. Please report an issue at 
    https://github.com/laoluadewoye/PKI_Practice_Python
            """
        )
    else:
        if args.manual_config_fp is not None:
            env_manual_settings: Union[dict, None] = parse_config_manual(args.manual_config_fp)
        else:
            env_manual_settings: Union[dict, None] = None

    # Check the return values for both
    assert env_auto_settings is not None, (
        """
Unparseable autoconfiguration file provided.
    Please ensure that your configuration file exists or are properly created.
    Use the default configuration files provided in the Default_Configs folder as a guide.
        """
    )

    if args.manual_config_fp is not None:
        assert env_manual_settings is not None, (
            """
Unparseable manual configuration file provided.
    Please ensure that your configuration file exists or are properly created.
    Use the default configuration files provided in the Default_Configs folder as a guide.
            """
        )

    return env_auto_settings, env_manual_settings


def start_program() -> None:
    """
    Starts the program. Used by RunConfig.py and command line call to start program.
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
    args, unknowns = parser.parse_known_args()

    # Start assertion region
    try:
        # Check if any unknown values were passed
        assert len(unknowns) == 0, (
            """
Warning: Unknown arguments provided. Please remove them from your command-line call.

Here are the valid options that can be passed.

-h or --help: Get help on how to use the program.
-a or --auto: The filepath of the auto configuration file.
-m or --manual: The filepath of the manual configuration file.
-t or --test: Run the program in test mode.
-d or --default: Run the program in default mode.
            """
        )

        # Check that either auto config file or default mode is provided
        assert args.auto_config_fp is not None or args.default_mode_on, (
            """
No auto configuration file or default switch is provided.

Please provide a configuration file by passing the filepath of your file as an command-line argument.
Otherwise, run the program in default mode.

Examples with passed auto config file:
    python RunConfig.py -a Default_Configs/default_auto.yaml
    run-pki-practice --auto Default_Configs/default_auto.yaml

Examples with default mode:
    python RunConfig.py -d
    run-pki-practice --default
            """
        )

        # Check if default mode is provided
        if args.default_mode_on:
            print(
                """
Default mode detected.
Welcome to PKI Practice!
This is not really meant for much, I just wanted to practice PKI architecture.
However, that does not mean that it should not be fun to play with.

In terms of command-line usage, you need to provide only two files.
The first is a config file for the auto generation of the environment using the -a or --auto flag.
The second is a config file for the manual configuration of the environment.
The second file is optional to run the program, but the first can be run without the second.

For more details, please run this command with the help option [-h | --help] 
or check out https://laoluadewoye.github.io/PKI_Practice_Python/.

For now though, here is a default run of the program using the example settings.
                
                """
            )

        # Read the configuration files or default configurations
        env_auto_settings, env_manual_settings = ingest_config(args)

        # Build the environment
        pki_network: Union[None, PKINetwork] = PKINetwork('Sample_Net', env_auto_settings, env_manual_settings)
        pki_network.set_root_certificates()

        # Go even further if not just testing the CLI options.
        if not args.test_mode_on:
            pki_network.start_network()
            pki_network.save_logs()

    # Ultimate error escape
    except AssertionError as e:
        print(f'\nException: {e}')
