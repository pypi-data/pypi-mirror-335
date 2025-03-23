# --------------------------------------------------------------------------------------------- #
""" Pyon: Numeric Encoder """
# --------------------------------------------------------------------------------------------- #

import logging

# --------------------------------------------------------------------------------------------- #

from decimal import Decimal

# --------------------------------------------------------------------------------------------- #

from ..utils import EConst
from ..supported_types import SupportedTypes

# --------------------------------------------------------------------------------------------- #

from .. import utils as ut

# --------------------------------------------------------------------------------------------- #

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------------- #


class NumEnc():
    """ Numeric Encoder """

    # ----------------------------------------------------------------------------------------- #

    def encode(self, value):
        """ Encodes the Entity object """

        # 1. ...
        encoded = None
        if self.is_encode(value):

            # 1.1 Complex...
            if isinstance(value, complex):
                encoded = self._encode_complex(value)

            # 1.2 Decimal...
            elif isinstance(value, Decimal):
                encoded = self._encode_decimal(value)

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

            # 1.1 Complex...
            if _type == SupportedTypes.COMPLEX.value:
                decoded = self._decode_complex(value)

            # 1.2 Decimal...
            elif _type == SupportedTypes.DECIMAL.value:
                decoded = self._decode_decimal(value)

        # 3. ...
        return decoded

    # ----------------------------------------------------------------------------------------- #

    def is_encode(self, value):
        """ 
            Checks if Numeric Types:
            - `complex`, `decimal.Decimal`
        """

        # 1. ...
        return isinstance(value, (Decimal, complex))

    # ----------------------------------------------------------------------------------------- #

    def is_decode(self, value):
        """ 
            Checks if Numeric Types:
            - `complex`, `decimal.Decimal`
        """

        # 1. ...
        is_decode = False

        # 2. ...
        if ut.is_decode_able(value):
            _type = value.get(EConst.TYPE)

            # 1.1 Checks...
            if _type in (
                SupportedTypes.COMPLEX.value,
                SupportedTypes.DECIMAL.value
            ):

                # 2.1 ...
                is_decode = True

        # 3. ...
        return is_decode

    # ----------------------------------------------------------------------------------------- #

    def _encode_complex(self, value: complex):
        """ Encodes the Complex Number """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, complex):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.COMPLEX.value,
                EConst.AUX1: value.real,
                EConst.AUX2: value.imag,
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: complex. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_complex(self, value: dict):
        """ Decodes to Complex number """

        # 1. Checks input...
        output = None
        if (
            (value is not None)
            and isinstance(value, dict)
            and (EConst.AUX1 in value)
            and (EConst.AUX2 in value)
        ):

            # 1.1 Decodes...
            output = complex(value[EConst.AUX1], value[EConst.AUX2])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid complex input. Expected: dict with %s and %s. Received: %s",
                EConst.AUX1,
                EConst.AUX2,
                type(value),
            )

        # 3. Returns...
        return output

# ----------------------------------------------------------------------------------------- #

    def _encode_decimal(self, value: Decimal):
        """ Encodes a Decimal object to a string representation. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, Decimal):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.DECIMAL.value,
                EConst.DATA: str(value)
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: Decimal. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_decimal(self, value: dict):
        """ Decodes a string representation back to a Decimal object. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = Decimal(value[EConst.DATA])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid decimal input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #


# --------------------------------------------------------------------------------------------- #
