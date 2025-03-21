"""
Module used for defining the holder class and it's functionality.
"""

from queue import Queue
from typing import Union
from time import sleep
from threading import Thread, Event
from datetime import datetime, timedelta
from random import uniform, seed
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from .SimUtils import hash_info, get_random_country_abbrv, get_random_division, create_private_key
from .Certificate import PKICertificate

import sys
from os.path import abspath, dirname, join
script_dir = dirname(abspath(__file__))
if script_dir in ['PKI_Practice', 'PKI Practice', 'app']:
    sys.path.append(abspath(script_dir))
elif script_dir == 'PKIPractice':
    sys.path.append(abspath(join(script_dir, '..')))
else:
    sys.path.append(abspath(join(script_dir, '../..')))

from PKIPractice.Utilities.DataclassUtils import *
from PKIPractice.Utilities.EnumUtils import auto_fill_types


class PKIHolder:
    """
    The PKIHolder class represents a public key infrastructure (PKI) holder.

    Attributes:
        holder_name (str): The name of the PKI holder.
        env_info (HOLDER_ENV_INFO): Environment-related information for the PKI holder, such as
            encryption algorithm, UID hash, and various durations.
        holder_type_info (HOLDER_TYPE_INFO): Information about the type of holder, such as hardware
            type, operating system details, and certification authority status.
        holder_info (HOLDER_INFO): General information about the holder, including name, location,
            organization, and contact details.
        holder_info_hash (str): Hash of the holder general information for secure identification.
        holder_priv_key (Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey]): The holder's private key.
        holder_pub_key (Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]): The holder's public key.
        holder_cert (Union[PKICertificate, None]): Placeholder for the holder's certificate.
        root_certs (dict[str, PKICertificate]): Dictionary storing root certificates.
        cached_certs (dict[str, tuple[datetime, PKICertificate]]): Cached certificates for quick access.
        cached_revocs (dict) : Cached revocations for quick access.
        csr_request_port (Queue): Queue for registration requests.
        csr_answer_port (Queue): Queue for registration answers.
        ocsp_request_port (Queue): Queue for OCSP requests.
        ocsp_answer_port (Queue): Queue for OCSP answers.
        reg_message_port (Queue): Queue for registration messages.
        has_self_cert (bool): Flag indicating whether the holder has a self-signed certificate.
        fresh_self_cert (bool): Flag indicating whether the holder has a fresh self-signed certificate.
        is_ca (bool): Indicates if the holder is a certification authority (CA).
        certificate_registry (dict): Stores certificates for lower-level entities.
        crl_registry (dict): Stores the certificate revocation list.

    Methods:
        get_addr() -> str:
            Returns the address of the holder.
        set_hub_conn(hub) -> None:
            Sets the hub connection of the holder.
        send_log(category, success, act, output, message) -> None:
            Sends log information to the Network hub for hub to publish to network logs.
        gen_self_cert() -> None:
            Generates a self-signed certificate if holder is a root CA.
        add_to_root_cache(root_url, root_cert) -> None:
            Adds passed root information and certificate to root cache.
        certificate_service(main_stop_event) -> None:
            Runs the local certificate management service for the holder.
        messaging_service(main_stop_event) -> None:
            Runs the local messenger service for the holder. Non-CAs only.
        ca_response_service(main_stop_event) -> None:
            Runs the local CA response service for the holder. CAs only.
        ca_revocation_service(main_stop_event) -> None:
            Runs the local CA revocation monitoring service for the holder. CAs only.
        start_holder(main_stop_event) -> None:
            Starts the holder's concurrent processes.
    """
    def __init__(self, holder_name: str, holder_config: dict, auto_config: dict):
        # Name of holder
        self.holder_name: str = holder_name

        level = holder_config['location']['level']

        # Environment information
        has_env_overrides = 'env_overrides' in holder_config.keys()
        if has_env_overrides and 'uid_hash' in holder_config['env_overrides'].keys():
            uid_hash = holder_config['env_overrides']['uid_hash']
        else:
            uid_hash = auto_config['uid_hash']

        if has_env_overrides and 'sig_hash' in holder_config['env_overrides'].keys():
            sig_hash = holder_config['env_overrides']['sig_hash']
        else:
            sig_hash = auto_config['sig_hash']

        if has_env_overrides and 'encrypt_alg' in holder_config['env_overrides'].keys():
            encrypt_alg = holder_config['env_overrides']['encrypt_alg']
        else:
            encrypt_alg = auto_config['encrypt_alg']

        if has_env_overrides and 'revoc_prob' in holder_config['env_overrides'].keys():
            revoc_prob = holder_config['env_overrides']['revoc_prob']
        else:
            revoc_prob = auto_config['revoc_probs'][level-1]

        if has_env_overrides and 'cert_valid_dur' in holder_config['env_overrides'].keys():
            cert_valid_dur = holder_config['env_overrides']['cert_valid_dur']
        else:
            cert_valid_dur = auto_config['cert_valid_durs'][level-1]
        if cert_valid_dur == 'none':
            cert_valid_dur = timedelta.max
        else:
            hours, minutes, seconds = map(int, cert_valid_dur.split(":"))
            cert_valid_dur = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        if has_env_overrides and 'cache_dur' in holder_config['env_overrides'].keys():
            cache_dur = holder_config['env_overrides']['cache_dur']
        else:
            cache_dur = auto_config['cache_durs'][level-1]
        if cache_dur == 'none':
            cache_dur = timedelta(seconds=0)
        else:
            minutes, seconds = map(int, cache_dur.split(":"))
            cache_dur = timedelta(minutes=minutes, seconds=seconds)

        if has_env_overrides and 'cooldown_dur' in holder_config['env_overrides'].keys():
            cooldown_dur = holder_config['env_overrides']['cooldown_dur']
        else:
            cooldown_dur = auto_config['cooldown_durs'][level-1]
        cooldown_dur = timedelta(seconds=int(cooldown_dur))

        if has_env_overrides and 'timeout_dur' in holder_config['env_overrides'].keys():
            timeout_dur = holder_config['env_overrides']['timeout_dur']
        else:
            timeout_dur = auto_config['timeout_durs'][level-1]
        timeout_dur = timedelta(seconds=int(timeout_dur))

        self.env_info: HOLDER_ENV_INFO = HOLDER_ENV_INFO(
            level=level, uid_hash=uid_hash, sig_hash=sig_hash, encrypt_alg=encrypt_alg, revoc_prob=revoc_prob,
            cert_valid_dur=cert_valid_dur, cache_dur=cache_dur, cooldown_dur=cooldown_dur, timeout_dur=timeout_dur
        )

        # Type information
        type_fill = [['', '', ''], ['', '', '', ''], ['', ''], ['']]
        has_holder_type = 'holder_type_info' in holder_config.keys()

        if level == 1:
            type_fill[3][0] = 'root_auth'
        elif level < auto_config['level_count']:
            type_fill[3][0] = 'inter_auth'
        else:
            type_fill[3][0] = 'not_auth'

        if has_holder_type:
            for key in holder_config['holder_type_info'].keys():
                if key == 'hardware_type':
                    type_fill[0][0] = holder_config['holder_type_info']['hardware_type']
                elif key == 'hardware_subtype':
                    type_fill[0][1] = holder_config['holder_type_info']['hardware_subtype']
                elif key == 'hardware_brand':
                    type_fill[0][2] = holder_config['holder_type_info']['hardware_brand']
                elif key == 'os_category':
                    type_fill[1][0] = holder_config['holder_type_info']['os_category']
                elif key == 'os_subcategory':
                    type_fill[1][1] = holder_config['holder_type_info']['os_subcategory']
                elif key == 'os_dist':
                    type_fill[1][2] = holder_config['holder_type_info']['os_dist']
                elif key == 'os_subdist':
                    type_fill[1][3] = holder_config['holder_type_info']['os_subdist']
                elif key == 'account_type':
                    type_fill[2][0] = holder_config['holder_type_info']['account_type']
                elif key == 'account_subtype':
                    type_fill[2][1] = holder_config['holder_type_info']['account_subtype']
                elif key == 'ca_status':
                    type_fill[3][0] = holder_config['holder_type_info']['ca_status']

        type_fill = auto_fill_types(type_fill)
        assert type_fill is not None, (
            f'Manual configuration type settings for {holder_name} were not valid.\n'
            f'\t   Settings in question: {holder_config["holder_type_info"]}.\n'
            '\t   Please check that the type configuration of the holder does not'
            ' violate any rules laid out in CONFIG_GUIDE.md and alter the settings.'
        )

        self.holder_type_info: HOLDER_TYPE_INFO = HOLDER_TYPE_INFO(
            hardware_type=type_fill[0][0],
            hardware_subtype=type_fill[0][1],
            hardware_brand=type_fill[0][2],
            os_category=type_fill[1][0],
            os_subcategory=type_fill[1][1],
            os_dist=type_fill[1][2],
            os_subdist=type_fill[1][3],
            account_type=type_fill[2][0],
            account_subtype=type_fill[2][1],
            ca_status=type_fill[3][0]
        )

        # Holder information
        has_holder_info = 'holder_info' in holder_config.keys()
        if has_holder_info and 'common_name' in holder_config['holder_info'].keys():
            common_name = holder_config['holder_info']['common_name']
        else:
            common_name = 'device_' + hash_info(self.holder_type_info.long_name, self.env_info.uid_hash)[:16]

        if has_holder_info and 'country' in holder_config['holder_info'].keys():
            country = holder_config['holder_info']['country']
        else:
            country = get_random_country_abbrv()

        if has_holder_info and 'state' in holder_config['holder_info'].keys():
            state = holder_config['holder_info']['state']
        else:
            state = 'State in ' + country

        if has_holder_info and 'locality' in holder_config['holder_info'].keys():
            locality = holder_config['holder_info']['locality']
        else:
            locality = 'Locality in ' + country

        if has_holder_info and 'org' in holder_config['holder_info'].keys():
            org = holder_config['holder_info']['org']
        else:
            org = common_name + "'s organization"

        if has_holder_info and 'org_unit' in holder_config['holder_info'].keys():
            org_unit = holder_config['holder_info']['org_unit']
        else:
            if self.holder_type_info.ca_status in ['inter_auth', 'root_auth']:
                org_unit = 'Certificates'
            else:
                org_unit = get_random_division()

        if has_holder_info and 'email' in holder_config['holder_info'].keys():
            email = holder_config['holder_info']['email']
            subdomain = email.split('@')[1]
        else:
            username = common_name.lower().replace(" ", "")
            subdomain = f'{org_unit.lower().replace(" ", "")}.theirorg.com'
            email = f'{username}@{subdomain}'

        if has_holder_info and 'url' in holder_config['holder_info'].keys():
            url = holder_config['holder_info']['url']
        else:
            if self.holder_type_info.ca_status == 'inter_auth':
                url = subdomain + '/intermediate_ca/' + common_name
            elif self.holder_type_info.ca_status == 'root_auth':
                url = subdomain + '/root_ca/' + common_name
            else:
                url = 'www.' + subdomain + '/' + common_name

        self.holder_info: HOLDER_INFO = HOLDER_INFO(
            common_name=common_name,
            country=country,
            state=state,
            local=locality,
            org=org,
            org_unit=org_unit,
            email=email,
            url=url
        )

        self.holder_info_hash: str = hash_info(self.holder_info.hash_content, self.env_info.uid_hash)

        # Create key pair
        self.holder_priv_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey] = create_private_key(
            self.env_info.encrypt_alg
        )
        self.holder_pub_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey] = self.holder_priv_key.public_key()

        # Creating certificate variables
        self.holder_cert: Union[PKICertificate, None] = None
        self.root_certs: dict[str, PKICertificate] = {}
        self.cached_certs: dict[str, tuple[datetime, PKICertificate]] = {}
        self.cached_revocs: dict = {}

        # Create ports
        self.csr_request_port: Queue = Queue(maxsize=50)
        self.csr_answer_port: Queue = Queue(maxsize=50)
        self.ocsp_request_port: Queue = Queue(maxsize=50)
        self.ocsp_answer_port: Queue = Queue(maxsize=50)
        self.reg_message_port: Queue = Queue(maxsize=50)

        # Create flags
        self.has_self_cert: bool = False
        self.fresh_self_cert: bool = False

        # Create CA-specific attributes
        if self.holder_type_info.ca_status in ['inter_auth', 'root_auth']:
            self.is_ca: bool = True
        else:
            self.is_ca: bool = False

        self.certificate_registry: dict = {}
        self.crl_registry: dict = {}

        # Create hub connection
        self.network_hub = None

    def get_addr(self) -> str:
        """
        Returns the url address of the holder.

        Returns:
            str: URL address of the holder.
        """

        return self.holder_info.url

    def set_hub_conn(self, hub) -> None:
        """
        Sets the connection to the hub.

        Args:
            hub: PKIHub - The hub to connect to.
        """

        self.network_hub = hub

        message: str = self.holder_name + ' has added a connection to the network hub.'
        self.send_log('Operations', True, 'Addition', 'Hub', message)

    def send_log(self, category: str, success: bool, act: str, output: str, message: str) -> None:
        """
        Sends a log message through the hub.

        Args:
            category: str - The category of the log entry.
            success: bool - If the action taken was successful.
            act: str - The action.
            output: str - The result of the action.
            message: str - The message with details of the actions.
        """

        self.network_hub.receive_log(category, success, act, output, self.holder_name, message)

    def gen_self_cert(self) -> Union[None, PKICertificate]:
        """
        Root-CAs can generate their own certificates, then send a message through the hub saying what was done.
        """

        if self.holder_type_info.ca_status != 'root_auth':
            # Send fail message
            message: str = self.holder_name + ' is not a root CA and cannot sign their own certificates.'
            self.send_log('PKI', False, 'Generation', 'Certificate', message)
            return None

        # Generate certificate with the name, subject information, issuer information,
        # environment information, subject public key, issuer private key
        cert_name: str = self.holder_name + 'Self Certificate'
        self.holder_cert = PKICertificate(
            cert_name, self.holder_info, self.holder_info,
            self.env_info, self.holder_pub_key, self.holder_priv_key
        )
        if self.holder_cert.error is not None:
            self.send_log(
                'PKI', False, 'Generation', 'Certificate',
                f'Error found when generating x509 certificate: {self.holder_cert.error}.'
            )

        if self.holder_cert is not None:
            message: str = 'The root CA ' + self.holder_name + ' has signed their own certificate.'
            self.send_log('PKI', True, 'Generation', 'Certificate', message)
            self.has_self_cert = True
            return self.holder_cert

        return None

    def add_to_root_cache(self, root_url: str, root_cert: PKICertificate) -> None:
        """
        Adds the root certificate to root certificate cache store.

        Args:
            root_url: str - The URL address of the root CA.
            root_cert: PKICertificate - The certificate of the root CA.
        """

        self.root_certs[root_url] = root_cert

        message: str = self.holder_name + ' has added the certificate of ' + root_url + ' to root cache store.'
        self.send_log('PKI', True, 'Addition', 'Certificate', message)

    def certificate_service(self, main_stop_event: Event) -> None:
        while not main_stop_event.is_set():
            # Seed the RNG for this turn
            seed(datetime.now().timestamp())

            # Check if self certificate exist
            if not self.has_self_cert:
                ...
                # If not, create a CSR and send it to the hub
                # If root CA, just generate a new one

                # When getting the response, validate the certificate signature and use chain of trust to validate more
                # When using chain of trust, do a signature check and an OCSP check. Save other certificates that pass

                # If it is not, skip the rest of this turn and try again

                # If it is, save the certificate as own
                # Turn on a temporary fresh cert flag
                self.fresh_self_cert = True

            # Check if self certificate is still valid with time comparison and RNG
            if not self.fresh_self_cert and self.has_self_cert:
                random_revoc = uniform(0, 1) < self.env_info.revoc_prob
                expired_cert = datetime.now() > self.holder_cert.valid_end
                if random_revoc or expired_cert:
                    # Revoke/Get renewed certificate and communicate that
                    ...

            # Turn off flag as it is not needed for the next turn
            self.fresh_self_cert = False

            # Check if there have been any messages in the CSR-Answer port if a certificate is needed
            if not self.csr_answer_port.empty() and not self.has_self_cert:
                # Certificates from CA are expected to be returned here.

                # Pop one message out.

                # Only process certificates if one is needed.
                # Check if it is valid and signed by all parties in CA chain.
                # If it's valid, save it as current holder certificate and send an acknowledgement message
                ...

            # Check if there have been any messages in the OCSP-Answer port
            if not self.ocsp_answer_port.empty():
                # OCSP notices from CA are expected to be returned here.

                # Pop one message out.

                # If there is a CRL notice, check if it's valid and signed by all parties in CA chain.
                # Also check if the certificate in question is actually in the list
                # If it's valid, save it to the CRL cache and send an acknowledgement message.
                # Reset the has_self_cert flag.
                ...

            # Sleep a random amount of time between 0 and 1 second
            sleep(uniform(0, 1))

    def messaging_service(self, main_stop_event: Event) -> None:
        while not main_stop_event.is_set():
            # Seed the RNG for this turn
            seed(datetime.now().timestamp())

            # Check if a certificate has not been obtained. If so, wait until the next turn
            if not self.has_self_cert:
                sleep(uniform(2, 5))
                continue

            # Check if there has been any messages in the message port
            if not self.reg_message_port.empty():
                # Messages from other non-CA holders are expected to be returned here.

                # Pop one message out.

                # If the message is signed, check that the certificate is valid
                # If so, process the message and send an acknowledgement
                ...

            # Send a random message to a random holder within the network layer

            # Sleep a random amount of time between 0 and 1 second
            sleep(uniform(0, 1))

    def ca_response_service(self, main_stop_event: Event) -> None:
        while not main_stop_event.is_set():
            # Seed the RNG for this turn
            seed(datetime.now().timestamp())

            # Check if there have been any messages in the CSR-Request port
            if not self.csr_request_port.empty():
                # CSRs from lower levels are expected to be in here.

                # Pop one message out.

                # Examine the CSR if it's valid and if so, return a certificate in the CSR-Answer port
                ...

            # Check if there have been any messages in the OCSP-Request port
            if not self.ocsp_request_port.empty():
                # OCSP Requests from lower levels are expected to be in here.

                # Pop one message out.

                # Examine the OCSP notice if it's valid and if so, return a OCSP Response in the OCSP-Answer port
                ...

            # Sleep a random amount of time between 0 and 1 second
            sleep(uniform(0, 1))

    def ca_revocation_service(self, main_stop_event: Event) -> None:
        while not main_stop_event.is_set():
            # Seed the RNG for this turn
            seed(datetime.now().timestamp())

            # Review certificate registry for possibly expired certificates
            # If a certificate is expired, add it to the revocation list and send revocation message

            # Sleep a random amount of time between 0 and 1 second
            sleep(uniform(0, 1))

    def start_holder(self, main_stop_event: Event) -> None:
        # Start Certificate Thread
        cert_thread = Thread(
            name=f'{self.holder_name}_cert_thread', target=self.certificate_service, args=(main_stop_event,),
            daemon=True
        )
        cert_thread.start()

        if not self.is_ca:
            # Start Regular Messaging Thread
            msg_thread = Thread(
                name=f'{self.holder_name}_msg_thread', target=self.messaging_service, args=(main_stop_event,),
                daemon=True
            )
            msg_thread.start()

        if self.is_ca:
            # Start CA Response Thread
            ca_rsp_thread = Thread(
                name=f'{self.holder_name}_ca_rsp_thread', target=self.ca_response_service, args=(main_stop_event,),
                daemon=True
            )
            ca_rsp_thread.start()

            # Start CA Registry Thread
            ca_reg_thread = Thread(
                name=f'{self.holder_name}_ca_crl_thread', target=self.ca_revocation_service, args=(main_stop_event,),
                daemon=True
            )
            ca_reg_thread.start()

        while not main_stop_event.is_set():
            sleep(1)
