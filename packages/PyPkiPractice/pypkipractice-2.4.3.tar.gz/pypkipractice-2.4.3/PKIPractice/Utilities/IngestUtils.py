"""
This file contains functions for parsing configuration files and validating their input.
"""

import sys
from typing import Union

# Specifying tomli library version
if sys.version_info[1] >= 11:
    import tomllib
else:
    import tomli

# Specifying yaml library version
if sys.version_info[1] > 9:
    import yaml

from xml.etree import ElementTree
import json
import re
from .EnumUtils import *


def parse_child_tags(xml_string: str) -> dict:
    """
    Parses the child tags of an XML string.

    Args:
        xml_string (str): The XML string to be parsed.

    Returns:
        dict: A dictionary containing the parsed child tags.
    """

    root = ElementTree.fromstring(xml_string)
    result = {}
    for child in root:
        if len(child) == 0 and child.tag not in result:  # New tag not come across inside parent tag
            result[child.tag] = child.text
        elif len(child) == 0 and isinstance(result[child.tag], str):  # Has come across a tag for the second time
            result[child.tag] = [result[child.tag], child.text]
        elif len(child) == 0 and isinstance(result[child.tag], list):  # Has come across a tag more than twice
            result[child.tag].append(child.text)
        else:  # Found a new parent tag
            result[child.tag] = parse_child_tags(ElementTree.tostring(child))
    return result


def adjust_types_auto(settings: dict) -> Union[dict, None]:
    """
    Adjusts the data types and format of the settings dictionary.

    Args:
        settings (dict): The dictionary to be modified and wrangled.

    Returns:
        dict: The tailored dictionary.
    """

    try:
        settings['level_count'] = int(settings['level_count'])
        settings['count_by_level'] = list(map(int, settings['count_by_level']))
        settings['uid_hash'] = settings['uid_hash'].lower().replace('-', '_')
        settings['sig_hash'] = settings['sig_hash'].lower().replace('-', '_')
        settings['encrypt_alg']['alg'] = settings['encrypt_alg']['alg'].lower()

        if settings['encrypt_alg']['alg'] == 'rsa':
            settings['encrypt_alg']['params']['pub_exp'] = int(settings['encrypt_alg']['params']['pub_exp'])
            settings['encrypt_alg']['params']['key_size'] = int(settings['encrypt_alg']['params']['key_size'])
        if settings['encrypt_alg']['alg'] == 'ecc':
            settings['encrypt_alg']['params']['curve'] = settings['encrypt_alg']['params']['curve'].lower()

        settings['revoc_probs'] = list(map(float, settings['revoc_probs']))
    except (KeyError, TypeError, ValueError) as e:
        topic = re.search(r"'(.*?)'", str(e)).group(1)
        print(
            f"""
Either "{topic}" is a missing key word, or "{topic}" is not the correct data type.

If the former is true, please add it to the configuration file.
If the latter is true, look for where it is used in the autoconfiguration file, as that is likely the 
    problem.
            """
        )
        return None

    return settings


def validate_settings_auto(settings: dict) -> bool:
    """
    Validates the settings dictionary.

    Args:
        settings (dict): The dictionary to be validated.

    Returns:
        bool: True if the settings are valid, False otherwise.
    """

    # Checking the existence and lengths of lists
    try:
        for setting in [
            settings['count_by_level'], settings['revoc_probs'], settings['cert_valid_durs'],
            settings['cache_durs'], settings['cooldown_durs'], settings['timeout_durs']
        ]:
            if not isinstance(setting, list):
                print(f'The value {setting} is not a list. Please fix this in the autoconfiguration file.')
                return False
            if len(setting) != settings['level_count']:
                print(f'The number of values in the list {setting} must match the level_count parameter. '
                      'Please fix this in the autoconfiguration file.')
                return False
    except KeyError as e:
        print(f'{e} is a missing key required in the autoconfiguration file. Please add it.')
        return False

    # Checking existence of untouched strings
    if not settings['uid_hash'] or not settings['sig_hash'] or not settings['encrypt_alg']['alg']:
        print('uid_hash, sig_hash, and encrypt_alg.alg are missing from the autoconfiguration file. Please add them.')
        return False

    # Checking durations for correct formats
    for i in range(len(settings['cert_valid_durs'])):
        dur = settings['cert_valid_durs'][i]
        if i == 0:
            if dur != 'none':
                print(f'"{dur}" is not a valid input for root CAs (first number) in '
                      f'cert_valid_durs. Please fix this in the autoconfiguration file.')
                return False
        else:
            if not (re.match(r'^[0-9]+:[0-9]{2}:[0-9]{2}$', dur) or dur == 'none'):
                print(
                    f'"{dur}" is not a valid input for cert_valid_durs. '
                    f'Please fix this in the autoconfiguration file.')
                return False

    for i in range(len(settings['cache_durs'])):
        dur = settings['cache_durs'][i]
        if i == 0:
            if dur != 'none':
                print(f'"{dur}" is not a valid input for root CAs (first number) in '
                      f'cert_valid_durs. Please fix this in the autoconfiguration file.')
                return False
        else:
            if not re.match(r'^[0-9]{2}:[0-9]{2}$', dur):
                print(
                    f'"{dur}" is not a valid input for cert_valid_durs. '
                    f'Please fix this in the autoconfiguration file.')
                return False

    for dur in settings['cooldown_durs']:
        if not re.match(r'^[0-9]+$', dur):
            print(f'"{dur}" is not a valid input for cooldown_durs. Please fix this in the autoconfiguration file.')
            return False

    for dur in settings['timeout_durs']:
        if not re.match(r'^[0-9]+$', dur):
            print(f'"{dur}" is not a valid input for timeout_durs. Please fix this in the autoconfiguration file.')
            return False

    # Checking if revoc_probs are between 0 and 1 inclusive
    for prob in settings['revoc_probs']:
        if prob < 0.0 or prob > 1.0:
            print(f'"{prob}" is not a valid input for revoc_probs and must be between 0 and 1. '
                  'Please fix this in the autoconfiguration file.')
            return False

    # Checking if parameters for hashing and encryption are valid
    if not has_value(SUPPORTED_HASH_ALGS, settings['uid_hash']):
        print(f'"{settings["uid_hash"]}" is not a valid input for uid_hash. Please fix this in the autoconfiguration ' 
              'file.')
        return False

    if not has_value(SUPPORTED_HASH_ALGS, settings['sig_hash']):
        print(f'"{settings["sig_hash"]}" is not a valid input for sig_hash. Please fix this in the autoconfiguration '
              'file.')
        return False

    if not has_value(SUPPORTED_ENCRYPT_ALGS, settings['encrypt_alg']['alg']):
        print(f'"{settings["encrypt_alg"]["alg"]}" is not a valid input for encrypt_alg.alg. Please fix this in the '
              'autoconfiguration file.')
        return False

    if settings['encrypt_alg']['alg'] == 'ecc':
        if not has_value(SUPPORTED_ECC_CURVES, settings['encrypt_alg']['params']['curve']):
            print(f'"{settings["encrypt_alg"]["params"]["curve"]}" is not a valid input for '
                  'encrypt_alg.params.curve. Please fix this in the autoconfiguration file.')
            return False

    # Checking if the program duration is in the correct format
    runtime_match = re.match(r'^[0-9]+:[0-9]{2}:[0-9]{2}$', settings['runtime'])
    runtime_none = settings['runtime'] == 'none'
    if not (runtime_match or runtime_none):
        print('Runtime parameter does not have a valid input for cert_valid_durs. '
              'Please fix this in the autoconfiguration file.')
        return False

    # Checking if a proper filepath is passed for the program.
    if 'log_save_filepath' not in settings.keys():
        print('The filepath for saving log files is not existent. Please add that to the autoconfiguration file.')
        return False

    if len(settings['log_save_filepath']) < 7:
        print('The filepath for saving log files is too short to be valid. '
              'File paths need to be at least 7 characters long. '
              'Please fix that in the autoconfiguration file.')
        return False

    if settings['log_save_filepath'][-4:] != '.csv':
        print('Invalid log file path found. '
              'Please ensure that the filepath you pass to the network has the ".csv" extension at the end. '
              'Logs are saved as CSV files for convenience. '
              'Please fix this in the autoconfiguration file.')
        return False

    # Checking if a proper database folder path is passed for the program.
    if 'db_folder_path' not in settings.keys():
        print('The filepath for saving database files is not existent. Please add that to the autoconfiguration file.')
        return False

    if len(settings['db_folder_path']) < 7:
        print('The filepath for saving database files is too short to be valid. '
              'File paths need to be at least 7 characters long. '
              'Please fix that in the autoconfiguration file.')
        return False

    if not bool(re.match(r'[\w/\\]', settings['db_folder_path'][-1])):
        print('Ending of database folder path is not valid. '
              'The end of the provided path must the last letter in the name or a slash to indicate a folder. '
              'Please fix this in the autoconfiguration file.')
        return False

    return True


def parse_config_auto(filepath: str) -> Union[dict, None]:
    """
    Parses an autoconfiguration file given its file path.

    Args:
        filepath (str): The path to the configuration file to be parsed.

    Returns:
        dict: A dictionary containing the parsed configuration data.
    """

    settings: Union[dict, None] = None

    # Check file type
    assert any(ext in filepath for ext in ['.yaml', '.yml', '.json', '.xml', '.toml']), (
        """
Invalid autoconfiguration configuration file provided.
    Please provide a configuration file that is a YAML, JSON, XML, or TOML file.
    Look in the Default_Configs folder for examples.
        """
    )

    # File type tree
    try:
        if filepath.endswith('.yaml') or filepath.endswith('.yml'):
            assert sys.version_info[1] > 9, (
                """
Using YAML files for configuration requires Python 3.10 or higher.
    Please update your Python version or use a different file format for configuration.
    Other supported examples are JSON, XML, or TOML.
    Look in the Default_Configs folder for examples.
                """
            )
            with open(filepath, 'r') as file:
                settings = yaml.load(file, Loader=yaml.Loader)
        elif filepath.endswith('.json'):
            with open(filepath, 'r') as file:
                settings = json.load(file)
        elif filepath.endswith('.xml'):
            with open(filepath, 'r') as file:
                settings = parse_child_tags(file.read())
        elif filepath.endswith('.toml'):
            if sys.version_info[1] >= 11:
                with open(filepath, 'rb') as file:
                    settings = tomllib.load(file)
            else:
                with open(filepath, 'rb') as file:
                    settings = tomli.load(file)
    except Exception as e:
        print(f'Ingestion libraries experienced an error: "{str(e).title()}"')
        return settings

    # Type adjustment
    settings = adjust_types_auto(settings)
    assert settings is not None, (
        """
Ingested autoconfiguration settings were not able to be adjusted due to incorrect configuration format.
    Please ensure your configuration file is correctly created.
    Use the default configuration file as a template.
        """
    )

    # Settings validation
    assert validate_settings_auto(settings) is True, (
        """
Ingested autoconfiguration settings were not found to be valid.
    Please ensure your configuration file is correctly created.
    Use the default configuration file as a template.
        """
    )

    return settings


def search_for_typecast_manual(settings: dict) -> Union[dict, None]:
    """
    Adjusts the data types and format of the settings dictionary.

    Args:
        settings (dict): The dictionary to be modified and wrangled.

    Returns:
        dict: The tailored dictionary.
    """

    try:
        for key, value in settings.items():
            if key in ['level', 'pub_exp', 'key_size']:
                settings[key] = int(value)
            elif key in ['revoc_prob']:
                settings[key] = float(value)
            elif isinstance(value, dict):
                settings[key] = search_for_typecast_manual(value)
                assert settings[key] is not None, (
                    """
Ingested manual configuration settings were not able to be adjusted due to incorrect 
    configuration format.
    
Please ensure your configuration file is correctly created.
Use the default configuration file as a template.
                    """
                )
        return settings
    except (KeyError, TypeError, ValueError) as e:
        print(e)
        match = re.search(r"'(.*?)'", str(e))
        if match:
            problematic_key = match.group(1)
            print(f'Look for where "{problematic_key}" is used in the manual configuration file, '
                  'as that is likely the problem.')


def parse_config_manual(filepath: str) -> Union[dict, None]:
    """
    Parses a manual configuration file given its file path.

    Args:
        filepath (str): The path to the configuration file to be parsed.

    Returns:
        dict: A dictionary containing the parsed configuration data.
    """

    settings: Union[dict, None] = None

    # Check file type
    assert any(ext in filepath for ext in ['.yaml', '.yml', '.json', '.xml', '.toml']), (
        """
Invalid manual configuration file provided.
    Please provide a configuration file that is a YAML, JSON, XML, or TOML file.
    Look in the Default_Configs folder for examples.
        """
    )

    # File type tree
    try:
        if filepath.endswith('.yaml') or filepath.endswith('.yml'):
            assert sys.version_info[1] > 9, (
                """
Using YAML files for configuration requires Python 3.10 or higher.
    Please update your Python version or use a different file format for configuration.
    Other supported examples are JSON, XML, or TOML.
    Look in the Default_Configs folder for examples.
                """
            )
            with open(filepath, 'r') as file:
                settings = yaml.load(file, Loader=yaml.Loader)
        elif filepath.endswith('.json'):
            with open(filepath, 'r') as file:
                settings = json.load(file)
        elif filepath.endswith('.xml'):
            with open(filepath, 'r') as file:
                settings = parse_child_tags(file.read())
        elif filepath.endswith('.toml'):
            if sys.version_info[1] >= 11:
                with open(filepath, 'rb') as file:
                    settings = tomllib.load(file)
            else:
                with open(filepath, 'rb') as file:
                    settings = tomli.load(file)
    except Exception as e:
        print(f'Ingestion libraries experienced an error: "{str(e).title()}"')
        return settings

    # Type adjustment
    settings = search_for_typecast_manual(settings)
    assert settings is not None, (
        """
Ingested manual configuration settings were not able to be adjusted due to unparsable configuration params.
    Please ensure your configuration file is correctly created.
    Use the default configuration file as a template.
        """
    )

    return settings
