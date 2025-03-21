"""
Module used for dataclass logic to store related information in each Holder.
"""

from dataclasses import dataclass
from datetime import timedelta


@dataclass
class HOLDER_ENV_INFO:
    """
    A class to represent environment information for the holder.

    Attributes:
        level (int): The security or access level of the holder.
        uid_hash (str): The hashed user identifier associated with the holder.
        sig_hash (str): The hashed signature associated with the holder.
        encrypt_alg (dict): A dictionary representing the encryption algorithm(s) used.
        revoc_prob (float): The probability of the certificate being revoked.
        cert_valid_dur (timedelta): The duration for which the certificate is valid.
        cache_dur (timedelta): The duration for which data is cached.
        cooldown_dur (timedelta): The cooldown duration between certain operations.
        timeout_dur (timedelta): The duration after which an operation times out.
    """

    level: int
    uid_hash: str
    sig_hash: str
    encrypt_alg: dict
    revoc_prob: float
    cert_valid_dur: timedelta
    cache_dur: timedelta
    cooldown_dur: timedelta
    timeout_dur: timedelta


@dataclass
class HOLDER_TYPE_INFO:
    """
    A class to represent information about the type of holder's environment.

    Attributes:
        hardware_type (str): The type of hardware (e.g., endpoint, appliance).
        hardware_subtype (str): The subtype of the hardware (e.g., laptop, server).
        hardware_brand (str): The brand of the hardware (e.g., Dell, Cisco).
        os_category (str): The category of the operating system (e.g., Windows, Unix).
        os_subcategory (str): The subcategory of the operating system (e.g., Linux, Solaris).
        os_dist (str): The distribution of the operating system (e.g., Ubuntu, Windows 10).
        os_subdist (str): The subdistribution of the operating system (e.g., Alpine, Standard).
        account_type (str): The type of account (e.g., admin, user).
        account_subtype (str): The subtype of the account (e.g., network admin, personal).
        ca_status (str): The certificate authority status (e.g., root auth, revoked).

    Methods:
        long_name() -> str:
            Returns a detailed, formatted string combining various environment attributes for identification.

        short_name() -> str:
            Returns a shortened, formatted string for a more concise identification.
    """

    hardware_type: str
    hardware_subtype: str
    hardware_brand: str
    os_category: str
    os_subcategory: str
    os_dist: str
    os_subdist: str
    account_type: str
    account_subtype: str
    ca_status: str

    @property
    def long_name(self) -> str:
        """
        Returns the long version of the holder's type information as a property.

        Returns:
            str: The combined string of everything.
        """

        return f'{self.hardware_type}_{self.hardware_subtype}_{self.hardware_brand}.' \
               f'{self.os_category}_{self.os_subcategory}_{self.os_dist}_{self.os_subdist}.' \
               f'{self.account_type}_{self.account_subtype}.{self.ca_status}'

    @property
    def short_name(self) -> str:
        """
        Returns the short version of the holder's type information as a property.

        Returns:
            str: The combined string of the key elements of type information.
        """

        return f'{self.hardware_brand}.{self.os_subdist}.{self.account_subtype}.{self.ca_status}'


@dataclass
class HOLDER_INFO:
    """
    A class to represent detailed information about a holder, typically used in certificate generation.

    Attributes:
        common_name (str): The common name of the holder (e.g., individual or organization name).
        country (str): The country of the holder.
        state (str): The state or region of the holder.
        local (str): The local or city of the holder.
        org (str): The organization of the holder.
        org_unit (str): The organizational unit or department within the organization.
        email (str): The email address of the holder.
        url (str): The URL associated with the holder.

    Methods:
        hash_content() -> str:
            Returns a concatenated string of the holder's attributes
            that can be used for hashing or generating a unique identifier.
    """

    common_name: str
    country: str
    state: str
    local: str
    org: str
    org_unit: str
    email: str
    url: str

    @property
    def hash_content(self) -> str:
        """
        Returns all the content of the holder information as a hashable string.
        """

        return f'{self.common_name}' \
               f'{self.country}{self.state}{self.local}' \
               f'{self.org}{self.org_unit}{self.email}{self.url}'


@dataclass
class SUBJECT_INFO:
    """
    A class to represent information about a certificate subject.

    Attributes:
        common_name (str): The common name of the holder (e.g., individual or organization name).
        country (str): The country of the holder.
        state (str): The state or region of the holder.
        local (str): The local or city of the holder.
        org (str): The organization of the holder.
        org_unit (str): The organizational unit or department within the organization.
        email (str): The email address of the holder.
        url (str): The URL associated with the holder.
    """

    common_name: str
    country: str
    state: str
    local: str
    org: str
    org_unit: str
    email: str
    url: str


@dataclass
class ISSUER_INFO:
    """
    A class to represent information about a certificate issuer.

    Attributes:
        common_name (str): The common name of the holder (e.g., individual or organization name).
        country (str): The country of the holder.
        state (str): The state or region of the holder.
        local (str): The local or city of the holder.
        org (str): The organization of the holder.
        url (str): The URL associated with the holder.
    """

    common_name: str
    country: str
    state: str
    local: str
    org: str
    url: str
