""" Pyon: Python Object Notation - Public Interface """
# --------------------------------------------------------------------------------------------- #

import json
import logging
import os

# --------------------------------------------------------------------------------------------- #

from .encoder import PyonEncoder

# --------------------------------------------------------------------------------------------- #

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------------- #


def encode(obj):
    """ Exports to pyon. """

    # 1. ...
    output = None
    if obj is not None:

        # 1.1 ...
        encoder = PyonEncoder()
        encoded = encoder.encode(obj)

        # 1.2 ...
        if encoded is not None:
            output = json.dumps(encoded, ensure_ascii=False, indent=3)

        # 1.3 ...
        else:
            logger.error("Object '%s' failed to be encoded.", type(obj).__name__)

    # 2. ...
    return output


# --------------------------------------------------------------------------------------------- #


def decode(pyon_str: str):
    """ Imports from pyon string. """

    # 1. ...
    output = None
    if pyon_str is not None:

        # 1.1 ...
        dictionary = json.loads(pyon_str)
        if dictionary is not None:

            # 2.1 ...
            encoder = PyonEncoder()
            output = encoder.decode(dictionary)

        # 1.2 ...
        else:
            logger.error("Input failed to be decoded.")

    # 2. ...
    return output


# --------------------------------------------------------------------------------------------- #


def to_file(obj, file_path: str = "./data.pyon", verbose: bool = True):
    """ Saves to file """

    # 1. ...
    pyon_text = encode(obj)

    # 2. ...
    if ((pyon_text is not None) and (len(pyon_text) > 0) and file_path
        and file_path.endswith(".pyon")):

        # 1.1 ...
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 1.2 ...
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(pyon_text)

        # 1.3 ...
        if verbose:
            logger.info("Data saved at %s", file_path)

    # 3. ...
    else:
        raise ValueError(f"Not a valid pyon output file: '{file_path}'")

    # 4. ...
    return pyon_text


# --------------------------------------------------------------------------------------------- #


def from_file(pyon_file_path):
    """ Imports from pyon file. """

    # 1. ...
    pyon_str = None
    if os.path.isfile(pyon_file_path):

        # 1.1. ...
        with open(file=pyon_file_path, mode="r", encoding="utf-8") as file:
            pyon_str = file.read()

    # 2. ...
    return decode(pyon_str)


# --------------------------------------------------------------------------------------------- #
