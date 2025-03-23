# --------------------------------------------------------------------------------------------- #
""" Pyon: Collections Encoder """
# --------------------------------------------------------------------------------------------- #

import base64
import logging

# --------------------------------------------------------------------------------------------- #

from collections import ChainMap, Counter, deque, defaultdict, namedtuple

# --------------------------------------------------------------------------------------------- #

from ..supported_types import SupportedTypes
from ..utils import EConst

# --------------------------------------------------------------------------------------------- #

from .. import utils as ut

# --------------------------------------------------------------------------------------------- #

from .base_encoder import BaseEncoder

# --------------------------------------------------------------------------------------------- #

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------------- #


class ColEnc(BaseEncoder):
    """ Collections Encoder """

    # ----------------------------------------------------------------------------------------- #

    def encode(self, value):
        """ Encodes the value """

        # 1. ...
        encoded = None
        if self.is_encode(value):

            # 1.1 Bytearray...
            if isinstance(value, bytearray):
                encoded = self._encode_bytearray(value)

            # 1.2 Bytes...
            elif isinstance(value, bytes):
                encoded = self._encode_bytes(value)

            # 1.3 ChainMap...
            elif isinstance(value, ChainMap):
                encoded = self._encode_chainmap(value)

            # 1.4 Counter...
            elif isinstance(value, Counter):
                encoded = self._encode_counter(value)

            # 1.5 Default Dict...
            elif isinstance(value, defaultdict):
                encoded = self._encode_defaultdict(value)

            # 1.6 Deque...
            elif isinstance(value, deque):
                encoded = self._encode_deque(value)

            # 1.7 Frozenset...
            elif isinstance(value, frozenset):
                encoded = self._encode_frozenset(value)

            # 1.8 List...
            elif isinstance(value, list):
                encoded = self._encode_list(value)

            # 1.9 NamedTuple...
            elif self._is_named_tuple(value):
                encoded = self._encode_namedtuple(value)

            # 1.10 Sets...
            elif isinstance(value, set):
                encoded = self._encode_set(value)

            # 1.11 Tuplas...
            elif isinstance(value, tuple):
                encoded = self._encode_tuple(value)

        # 2. ...
        return encoded

    # ----------------------------------------------------------------------------------------- #

    def decode(self, value):
        """ Decodes the value """

        # 1. ...
        decoded = None

        # 2. ...
        if ut.is_decode_able(value):
            _type = value.get(EConst.TYPE)

            # 1.1 Bytearray...
            if _type == SupportedTypes.BYTEARRAY.value:
                decoded = self._decode_bytearray(value)

            # 1.2 Bytes...
            elif _type == SupportedTypes.BYTES.value:
                decoded = self._decode_bytes(value)

            # 1.3 ChainMap...
            elif _type == SupportedTypes.CHAINMAP.value:
                decoded = self._decode_chainmap(value)

            # 1.4 Counter...
            elif _type == SupportedTypes.COUNTER.value:
                decoded = self._decode_counter(value)

            # 1.5 Default Dict...
            elif _type == SupportedTypes.DEFAULTDICT.value:
                decoded = self._decode_defaultdict(value)

            # 1.6 Deque...
            elif _type == SupportedTypes.DEQUE.value:
                decoded = self._decode_deque(value)

            # 1.7 Frozenset...
            elif _type == SupportedTypes.FROZENSET.value:
                decoded = self._decode_frozenset(value)

            # 1.8 List...
            elif _type == SupportedTypes.LIST.value:
                decoded = self._decode_list(value)

            # 1.9 NamedTuple...
            elif _type == SupportedTypes.NAMEDTUPLE.value:
                decoded = self._decode_namedtuple(value)

            # 1.10 Sets...
            elif _type == SupportedTypes.SET.value:
                decoded = self._decode_set(value)

            # 1.11  Tuples...
            elif _type == SupportedTypes.TUPLE.value:
                decoded = self._decode_tuple(value)

        # 3. ...
        return decoded

    # ----------------------------------------------------------------------------------------- #

    def is_encode(self, value):
        """ 
            Checks if Collection Types:
            - `bytearray`, `bytes`, `frozenset`, `list`, `set`, `tuple`
            - `ChainMap`, `Counter`, `defaultdict`, `deque`, `namedtuple` (from collections)
        """

        # 1. ...
        return isinstance(
            value,
            (
                bytearray, bytes, frozenset, list, set, tuple,
                ChainMap, Counter, defaultdict, deque
            )
        )

    # ----------------------------------------------------------------------------------------- #

    def is_decode(self, value):
        """ 
            Checks if Collection Types:
            - `bytearray`, `bytes`, `frozenset`, `list`, `set`, `tuple`
            - `ChainMap`, `Counter`, `defaultdict`, `deque`, `namedtuple` (from collections)
        """

        # 1. ...
        is_decode = False

        # 2. ...
        if ut.is_decode_able(value):
            _type = value.get(EConst.TYPE)

            # 1.1 Checks...
            if _type in (
                SupportedTypes.BYTEARRAY.value,
                SupportedTypes.BYTES.value,
                SupportedTypes.CHAINMAP.value,
                SupportedTypes.COUNTER.value,
                SupportedTypes.DEFAULTDICT.value,
                SupportedTypes.DEQUE.value,
                SupportedTypes.FROZENSET.value,
                SupportedTypes.LIST.value,
                SupportedTypes.NAMEDTUPLE.value,
                SupportedTypes.SET.value,
                SupportedTypes.TUPLE.value
            ):

                # 2.1 ...
                is_decode = True

        # 3. ...
        return is_decode

    # ----------------------------------------------------------------------------------------- #

    def _is_named_tuple(self, value):
        """ If `value` is a named tuple """

        # 1. ...
        return isinstance(value, tuple) and hasattr(value, EConst.FIELDS)

    # ----------------------------------------------------------------------------------------- #

    def _encode_bytearray(self, value: bytearray):
        """ Encodes a bytearray to a Base64 string """

        # 1. ...
        output = None
        if (value is not None) and isinstance(value, bytearray):

            # 1.1 ...
            output = {
                EConst.TYPE: SupportedTypes.BYTEARRAY.value,
                EConst.DATA: base64.b64encode(value).decode('utf-8')
            }

        # 2. ...
        else:
            logger.error("Invalid input. Expected: bytearray. Received: %s", type(value))

        # 3. ...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_bytearray(self, value: dict):
        """ Decodes a Base64 string back to bytearray """

        # 1. ...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 ...
            output = bytearray(base64.b64decode(value[EConst.DATA]))

        # 2. ...
        else:

            # 1.1 ...
            logger.error(
                "Invalid bytearray input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. ...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_bytes(self, value: bytes):
        """ Encodes bytes to a Base64 string """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, bytes):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.BYTES.value,
                EConst.DATA: base64.b64encode(value).decode('utf-8')
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: bytes. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_bytes(self, value: dict):
        """ Decodes a Base64 string back to bytes """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = base64.b64decode(value[EConst.DATA])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid bytes input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_chainmap(self, value: ChainMap):
        """ Encodes a ChainMap object to a list of dictionaries. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, ChainMap):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.CHAINMAP.value,
                EConst.DATA: [
                    {k: self._encode(v) for k, v in m.items()}
                    for m in value.maps
                ]
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: ChainMap. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_chainmap(self, value: dict):
        """ Decodes a list of dictionaries back to a ChainMap object. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Reconstructs...
            maps = [
                {k: self._decode(v) for k, v in m.items()}
                for m in value[EConst.DATA]
            ]

            # 1.2 Decodes...
            output = ChainMap(*maps)

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid chainmap input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_counter(self, value: Counter):
        """ Encodes a Counter object to a dictionary representation. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, Counter):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.COUNTER.value,
                EConst.DATA: {k: self._encode(v) for k, v in value.items()}
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: Counter. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_counter(self, value: dict):
        """ Decodes a dictionary representation back to a Counter object. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            decoded_data = {k: self._decode(v) for k, v in value[EConst.DATA].items()}
            output = Counter(decoded_data)

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid counter input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_defaultdict(self, value: defaultdict):
        """ Encodes a defaultdict object to a dictionary representation. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, defaultdict):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.DEFAULTDICT.value,
                EConst.AUX1: ut.get_class_name(value.default_factory),
                EConst.DATA: {k: self._encode(v) for k, v in value.items()}
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: defaultdict. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_defaultdict(self, value: dict):
        """ Decodes a dictionary representation back to a defaultdict object. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Default...
            default_factory = None

            # 1.2 Reconstructs...
            if (EConst.AUX1 in value) and value[EConst.AUX1]:
                default_factory = ut.get_class({EConst.CLASS: value[EConst.AUX1]})

            # 1.3 Decodes...
            decoded_data = {k: self._decode(v) for k, v in value[EConst.DATA].items()}
            output = defaultdict(default_factory, decoded_data)

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid defaultdict input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_deque(self, value: deque):
        """ Encodes a deque object to a list representation. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, deque):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.DEQUE.value,
                EConst.DATA: [self._encode(item) for item in value]
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: deque. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_deque(self, value: dict):
        """ Decodes a list representation back to a deque object. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = deque([self._decode(item) for item in value[EConst.DATA]])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid deque input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_frozenset(self, value: frozenset):
        """ Encodes a frozenset object to a list representation. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, frozenset):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.FROZENSET.value,
                EConst.DATA: [self._encode(item) for item in value]
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: frozenset. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_frozenset(self, value: dict):
        """ Decodes a list representation back to a frozenset object. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = frozenset([self._decode(item) for item in value[EConst.DATA]])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid frozenset input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_list(self, value: list):
        """ Encodes the List """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, list):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.LIST.value,
                EConst.DATA: [self._encode(item) for item in value]
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: set. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_list(self, value: list):
        """ Decodes to List """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = [self._decode(item) for item in value[EConst.DATA]]

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid set input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_namedtuple(self, value: namedtuple):
        """ Encodes a namedtuple object to a dictionary representation. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, tuple) and hasattr(value, EConst.FIELDS):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.NAMEDTUPLE.value,
                EConst.CLASS: ut.get_class_name(value),
                EConst.DATA: {
                    field: self._encode(getattr(value, field))
                    for field in value._fields
                },
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: namedtuple. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_namedtuple(self, value: dict):
        """ Decodes a dictionary representation back to a namedtuple object. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Reconstructs...
            cls_namedtuple = ut.get_class(value)
            if cls_namedtuple is not None:

                # 2.1 Decodes individual fields...
                decoded_data = {
                    key: self._decode(val) for key, val in value[EConst.DATA].items()
                }

                # 2.2 Creates the namedtuple...
                output = cls_namedtuple(**decoded_data)

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid namedtuple input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_set(self, value: set):
        """ Encodes the Set """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, set):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.SET.value,
                EConst.DATA: [self._encode(item) for item in value]
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: set. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_set(self, value: dict):
        """ Decodes to Set """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = {self._decode(item) for item in value[EConst.DATA]}

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid set input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_tuple(self, value: tuple):
        """ Encodes the Tuple """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, tuple):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.TUPLE.value,
                EConst.DATA: [self._encode(item) for item in value]
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: tuple. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_tuple(self, value: dict):
        """ Decodes to Tuple """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = tuple(self._decode(item) for item in value[EConst.DATA])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid tuple input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #


# --------------------------------------------------------------------------------------------- #
