# --------------------------------------------------------------------------------------------- #
""" Pyon: Datetime Encoder """
# --------------------------------------------------------------------------------------------- #

import logging

# --------------------------------------------------------------------------------------------- #

from datetime import datetime, date, time

# --------------------------------------------------------------------------------------------- #

from ..utils import EConst
from ..supported_types import SupportedTypes

# --------------------------------------------------------------------------------------------- #

from .. import utils as ut

# --------------------------------------------------------------------------------------------- #

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------------- #


class DateEnc():
    """ Pyon Encoder """

    # ----------------------------------------------------------------------------------------- #

    def encode(self, value):
        """ Encodes the Entity object """

        # 1. ...
        encoded = None
        if self.is_encode(value):

            # 1.1 Datetime...
            if isinstance(value, datetime):
                encoded = self._encode_datetime(value)

            # 1.2 Date...
            elif isinstance(value, date):
                encoded = self._encode_date(value)

            # 1.3 Time...
            elif isinstance(value, time):
                encoded = self._encode_time(value)

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

            # 1.1 Date...
            if _type == SupportedTypes.DATE.value:
                decoded = self._decode_date(value)

            # 1.2 Datetime...
            elif _type == SupportedTypes.DATETIME.value:
                decoded = self._decode_datetime(value)

            # 1.3 Time...
            elif _type == SupportedTypes.TIME.value:
                decoded = self._decode_time(value)

        # 3. ...
        return decoded

    # ----------------------------------------------------------------------------------------- #

    def is_encode(self, value):
        """ 
            Checks if Datetime Types:
            - `datetime.date`, `datetime.datetime`, `datetime.time`
        """

        # 1. ...
        return isinstance(value, (date, datetime, time))

    # ----------------------------------------------------------------------------------------- #

    def is_decode(self, value):
        """ 
            Checks if Datetime Types:
            - `datetime.date`, `datetime.datetime`, `datetime.time`
        """

        # 1. ...
        is_decode = False

        # 2. ...
        if ut.is_decode_able(value):
            _type = value.get(EConst.TYPE)

            # 1.1 Checks...
            if _type in (
                SupportedTypes.DATE.value,
                SupportedTypes.DATETIME.value,
                SupportedTypes.TIME.value
            ):

                # 2.1 ...
                is_decode = True

        # 3. ...
        return is_decode

    # ----------------------------------------------------------------------------------------- #

    def _encode_date(self, value: date):
        """ Encodes a date object to ISO 8601 format. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, date):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.DATE.value,
                EConst.DATA: value.isoformat()
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: date. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_date(self, value: dict):
        """ Decodes an ISO 8601 string back to a date object. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = date.fromisoformat(value[EConst.DATA])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid date input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_datetime(self, value: datetime):
        """ Encodes a datetime object to ISO 8601 format. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, datetime):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.DATETIME.value,
                EConst.DATA: value.isoformat()
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: datetime. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_datetime(self, value: dict):
        """ Decodes an ISO 8601 string back to a datetime object. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = datetime.fromisoformat(value[EConst.DATA])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid datetime input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_time(self, value: time):
        """ Encodes a time object to ISO 8601 format. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, time):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.TIME.value,
                EConst.DATA: value.isoformat()
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: time. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_time(self, value: dict):
        """ Decodes an ISO 8601 string back to a time object. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = time.fromisoformat(value[EConst.DATA])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid time input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #


# --------------------------------------------------------------------------------------------- #
