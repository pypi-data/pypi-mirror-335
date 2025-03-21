"""
Simulation specific utilities that make more sense to keep outside classes.
"""

import random
from typing import Union
from cryptography.hazmat.primitives.hashes import *
from cryptography.hazmat.primitives.asymmetric import rsa, ec


def hash_info(information: str, hash_func_string: str) -> str:
    """
    Uses the established hash string to hash whatever information is passed.
    Raises an error if the choice is unsupported.

    Args:
        information: str - Any information as long as it is in string format.
        hash_func_string: str - The (assumingly acceptable) hash of choice.

    Returns:
        str: The hashed information if choice is valid.
    """

    if hash_func_string == 'sha224':
        digest: Hash = Hash(SHA224())
    elif hash_func_string == 'sha256':
        digest: Hash = Hash(SHA256())
    elif hash_func_string == 'sha384':
        digest: Hash = Hash(SHA384())
    elif hash_func_string == 'sha512':
        digest: Hash = Hash(SHA512())
    elif hash_func_string == 'sha3_224':
        digest: Hash = Hash(SHA3_224())
    elif hash_func_string == 'sha3_256':
        digest: Hash = Hash(SHA3_256())
    elif hash_func_string == 'sha3_384':
        digest: Hash = Hash(SHA3_384())
    elif hash_func_string == 'sha3_512':
        digest: Hash = Hash(SHA3_512())
    elif hash_func_string == 'blake2b':
        digest: Hash = Hash(BLAKE2b(64))
    elif hash_func_string == 'blake2s':
        digest: Hash = Hash(BLAKE2s(32))
    else:
        raise ValueError(f"Unsupported hash: {hash_func_string}")

    digest.update(information.encode('utf-8'))
    return digest.finalize().hex()


def get_hash_func(hash_func_string: str) -> HashAlgorithm:
    """
    Returns a hash algorithm object corresponding to the hash passed in.

    Args:
        hash_func_string: str - The (assumingly acceptable) hash of choice.

    Returns:
        HashAlgorithm: The hashing object to use.
    """

    if hash_func_string == 'sha224':
        return SHA224()
    elif hash_func_string == 'sha256':
        return SHA256()
    elif hash_func_string == 'sha384':
        return SHA384()
    elif hash_func_string == 'sha512':
        return SHA512()
    elif hash_func_string == 'sha3_224':
        return SHA3_224()
    elif hash_func_string == 'sha3_256':
        return SHA3_256()
    elif hash_func_string == 'sha3_384':
        return SHA3_384()
    elif hash_func_string == 'sha3_512':
        return SHA3_512()
    elif hash_func_string == 'blake2b':
        return BLAKE2b(64)
    elif hash_func_string == 'blake2s':
        return BLAKE2s(32)
    else:
        raise ValueError(f"Unsupported hash: {hash_func_string}")


def get_random_country() -> str:
    """
    Retrieves a random country from a list of countries.

    Returns:
        str: The random country chosen.
    """

    countries: tuple = (
        "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia",
        "Australia", "Austria", "Azerbaijan", "The Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium",
        "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria",
        "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad",
        "Chile", "China", "Colombia", "Comoros", "Congo, Democratic Republic of the", "Congo, Republic of the",
        "Costa Rica", "Côte d’Ivoire", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti",
        "Dominica", "Dominican Republic", "East Timor (Timor-Leste)", "Ecuador", "Egypt", "El Salvador",
        "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon",
        "The Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
        "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel",
        "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, North", "Korea, South",
        "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein",
        "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
        "Mauritania", "Mauritius", "Mexico", "Micronesia, Federated States of", "Moldova", "Monaco", "Mongolia",
        "Montenegro", "Morocco", "Mozambique", "Myanmar (Burma)", "Namibia", "Nauru", "Nepal", "Netherlands",
        "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau",
        "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania",
        "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa",
        "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone",
        "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "Spain", "Sri Lanka",
        "Sudan", "South Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania",
        "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda",
        "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu",
        "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
    )

    return random.choice(countries)


def get_random_country_abbrv() -> str:
    """
    Retrieves a random country abbreviation from a list of countries.

    Returns:
        str: The random country chosen.
    """

    countries: tuple = (
        "AF", "AL", "DZ", "AD", "AO", "AG", "AR", "AM",
        "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE",
        "BZ", "BJ", "BT", "BO", "BA", "BW", "BR", "BN", "BG",
        "BF", "BI", "CV", "KH", "CM", "CA", "CF", "TD",
        "CL", "CN", "CO", "KM", "CD", "CG",
        "CR", "CI", "HR", "CU", "CY", "CZ", "DK", "DJ",
        "DM", "DO", "TL", "EC", "EG", "SV",
        "GQ", "ER", "EE", "SZ", "ET", "FJ", "FI", "FR", "GA",
        "GM", "GE", "DE", "GH", "GR", "GD", "GT", "GN", "GW",
        "GY", "HT", "HN", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IL",
        "IT", "JM", "JP", "JO", "KZ", "KE", "KI", "KP", "KR",
        "XK", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI",
        "LT", "LU", "MG", "MW", "MY", "MV", "ML", "MT", "MH",
        "MR", "MU", "MX", "FM", "MD", "MC", "MN",
        "ME", "MA", "MZ", "MM", "NA", "NR", "NP", "NL",
        "NZ", "NI", "NE", "NG", "MK", "NO", "OM", "PK", "PW",
        "PA", "PG", "PY", "PE", "PH", "PL", "PT", "QA", "RO",
        "RU", "RW", "KN", "LC", "VC", "WS",
        "SM", "ST", "SA", "SN", "RS", "SC", "SL",
        "SG", "SK", "SI", "SB", "SO", "ZA", "ES", "LK",
        "SD", "SS", "SR", "SE", "CH", "SY", "TW", "TJ", "TZ",
        "TH", "TG", "TO", "TT", "TN", "TR", "TM", "TV", "UG",
        "UA", "AE", "GB", "US", "UY", "UZ", "VU",
        "VA", "VE", "VN", "YE", "ZM", "ZW"
    )

    return random.choice(countries)


def get_random_division() -> str:
    """
    Retrieves a random business division from a list of divisions.

    Returns:
        str: The random business division chosen.
    """

    business_units: tuple = (
        "Human Resources", "Finance", "Accounting", "Marketing", "Sales", "Operations", "IT (Information Technology)",
        "Research and Development (R&D)", "Customer Service", "Legal", "Procurement", "Supply Chain Management",
        "Production", "Quality Assurance", "Public Relations (PR)", "Business Development", "Strategy and Planning",
        "Compliance", "Data Analytics", "Training and Development", "Facilities Management", "Risk Management",
        "Corporate Social Responsibility (CSR)", "Internal Audit", "Engineering", "Product Management",
        "Executive Management", "Investor Relations", "Logistics", "Security", "Operations Management"
    )

    return random.choice(business_units)


def get_curve(holder_curve: str) -> ec.EllipticCurve:
    """
    Takes a passed curve and returns a curve object, or raises an error if the curve is unsupported.

    Args:
        holder_curve: str - The passed curve choice.

    Returns:
        ec.EllipticCurve: The elliptic curve object.
    """

    if holder_curve == 'secp256r1':
        return ec.SECP256R1()
    elif holder_curve == 'secp384r1':
        return ec.SECP384R1()
    elif holder_curve == 'secp521r1':
        return ec.SECP521R1()
    elif holder_curve == 'secp224r1':
        return ec.SECP224R1()
    elif holder_curve == 'secp192r1':
        return ec.SECP192R1()
    elif holder_curve == 'secp256k1':
        return ec.SECP256K1()
    else:
        raise ValueError(f"Unsupported curve: {holder_curve}")


def create_private_key(holder_encrypt_alg: dict) -> Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey]:
    """
    Takes encryption algorithm parameters and returns either a private key or Nothing.

    Args:
        holder_encrypt_alg: dict - dictionary of encryption algorithm settings

    Returns:
        Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey, None]: The private key or lack of one.
    """

    params: dict = holder_encrypt_alg['params']
    try:
        if holder_encrypt_alg['alg'] == 'rsa':
            return rsa.generate_private_key(public_exponent=params['pub_exp'], key_size=params['key_size'])
        elif holder_encrypt_alg['alg'] == 'ecc':
            curve: ec.EllipticCurve = get_curve(params['curve'])
            return ec.generate_private_key(curve=curve)
    except ValueError as e:
        assert False, (
            'Incorrect value detected during Holder creation.\n' 
            f'\t   Message: {e}.\n'
            '\t   Please check automatic or manual configuration files that contain the passed value.'
        )
