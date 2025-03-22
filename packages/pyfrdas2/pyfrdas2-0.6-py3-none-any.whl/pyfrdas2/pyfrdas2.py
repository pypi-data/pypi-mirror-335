# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# Licence LGPL-2.1 or later (https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html).

import logging
from datetime import datetime
import pgpy
import gzip
import re
from unidecode import unidecode
# I decided NOT to use importlib.resources which is supposed to replace
# pkg_resources, because their interface changes too much among python version
# and I don't want to be bothered by interfaces different in 3.11
from pkg_resources import resource_filename
import importlib.metadata
from .fantoir import FANTOIR_MAP


VERSION = importlib.metadata.version("pyfrdas2")
FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('pyfrdas2')
logger.setLevel(logging.INFO)


def get_partner_declaration_threshold(year):
    if not isinstance(year, int):
        raise ValueError("year must be an integer")
    # threshold updated from 1200 € to 2400 € from decl 2025 for year 2024
    # https://bofip.impots.gouv.fr/bofip/14327-PGP.html/ACTU-2024-00154
    if year < 2024:
        return 1200
    return 2400


def generate_file(file_bytes, year, siren, encryption="prod"):
    logger.debug(
        'generate_file with year=%s, siren=%s and encryption=%s',
        year, siren, encryption)
    logger.debug('using pyfrdas2 version %s', VERSION)
    if encryption not in ("prod", "test", "none"):
        raise ValueError("Wrong value for encryption argument.")
    if not isinstance(year, int):
        raise ValueError("The year argument must be an integer.")
    if year < 2023:
        raise ValueError("The year argument must be 2023 or higher.")
    if not isinstance(siren, str):
        raise ValueError("The siren argument must be a string.")
    siren = siren.replace(" ", "")
    if len(siren) != 9 or not siren.isdigit():
        raise ValueError("The siren argument must be a string of 9 digits.")
    if not isinstance(file_bytes, bytes):
        raise ValueError("The file_bytes argument must be a bytes.")
    key_year = year
    if key_year == 2024:  # keys unchanged in 2024
        key_year = 2023
    if encryption in ("prod", "test"):
        prefix = "DSAL_"
        file_ext = "txt.gz.gpg"
        encryption_up = encryption.upper()
        key_filename = f'{key_year}-DGFIP_TIERSDECLARANTS_{encryption_up}.asc'
        key_path = resource_filename(__name__, f'pgp_keys/{key_filename}')
        logger.debug('Encryption key path is %s', key_path)
        try:
            with open(key_path, mode="rb") as key_file:
                key_file_blob = key_file.read()
        except FileNotFoundError as e:
            raise ValueError(
                f"The DAS2 encryption key is not available for year {year} "
                f"(file '{key_filename}' is not available in the python library "
                f"pyfrdas2 version {VERSION}). Try to upgrade the library."
            ) from e
        pubkey = pgpy.PGPKey.from_blob(key_file_blob)[0]
        file_content_compressed = gzip.compress(file_bytes)
        to_encrypt_object = pgpy.PGPMessage.new(file_content_compressed)
        file_bytes_result = bytes(pubkey.encrypt(to_encrypt_object))
    else:
        file_bytes_result = file_bytes
        prefix = "UNENCRYPTED_DAS2_for_audit-"
        file_ext = "txt"

    filename = "%(prefix)s%(year)s_%(siren)s_000_%(gentime)s.%(file_ext)s" % {
        "prefix": prefix,
        "year": year,
        "siren": siren,
        "gentime": datetime.now().strftime("%Y%m%d%H%M%S"),
        "file_ext": file_ext,
    }
    logger.info('Successfully generated DAS2 file %s', filename)
    return (file_bytes_result, filename)


def format_street_block(street):
    logger.debug("format_street_block called with argument '%s'", street)
    street = street and street.strip()
    if not street:
        return _format_field("0000", 32)
    street = street.replace(",", " ")
    street = street.replace(".", " ")
    # replace all multi-spaces by one space
    street = " ".join(street.split())

    # replace abbreviations by complete word
    abbrev = {
        "av": "avenue",
        "bd": "boulevard",
        "bld": "boulevard",
        "ch": "chemin",
        "all": "allée",
    }
    for short, long in abbrev.items():
        pattern = re.compile(f" {short} ", re.IGNORECASE)
        street = pattern.sub(f" {long} ", street)

    bis = " "
    bismap = {  # keys have a space as final letter
        "bis": "B",
        "ter": "T",
        "quarter": "Q",
    }

    # split on digit
    ini_street = street
    for _index, char in enumerate(street):
        if not char.isdigit():
            break
    number = street[:_index]
    # remove leading zeros
    number_int = int(number or 0)
    street = street[_index:].strip()
    if len(str(number)) > 4:
        number_int = 0
        street = ini_street
    street_lower = street.lower()
    for bis_entry, bis_char in bismap.items():
        if street_lower.startswith(bis_entry + " "):
            bis = bis_char
            street = street[len(bis_entry) + 1:]
    # if 1 letter and space
    if len(street) > 2 and list(street)[0].isalpha() and list(street)[1] == " ":
        bis = list(street)[0]
        street = street[2:]

    fantoir_map = {}
    for street_type, code in FANTOIR_MAP.items():
        fantoir_map[unidecode(street_type).lower()] = code

    street_type_code = ""
    street_lower_uni = unidecode(street).lower()
    for street_type, code in fantoir_map.items():
        if street_lower_uni.startswith(street_type + " "):
            street_type_code = code
            street = street[len(street_type) + 1:]
            break

    if len(street) > 21:
        street = street[-21:]
    number_formatted = _format_field(number_int, 4)
    street_formatted = _format_field(street, 21)
    street_type_code_formatted = _format_field(street_type_code, 4)
    cstreet = f'{number_formatted}{bis} {street_type_code_formatted} {street_formatted}'
    if len(cstreet) != 32:
        raise ValueError(
            f"The street block '{cstreet}' should be 32 characters long "
            f"(current lenght is {len(cstreet)}). "
            f"This error should never happen.")
    logger.debug('Format street block result: %s', cstreet)
    return cstreet


def _format_field(value, size):
    if isinstance(value, int):
        value = str(value)
        if len(value) > size:
            raise ValueError(
                f"Integer {value} should not have more than {size} digits. "
                f"This should never happen.")
        if len(value) < size:
            value = value.rjust(size, "0")
        return value
    if not value:
        value = " " * size
    # Cut if too long
    value = value[0:size]
    # enlarge if too small
    if len(value) < size:
        value = value.ljust(size, " ")
    return value
