# --------------------------------------------------------------------------------------------- #
""" Pyon: Specialized Encoder """
# --------------------------------------------------------------------------------------------- #

import logging

# --------------------------------------------------------------------------------------------- #

from uuid import UUID

# --------------------------------------------------------------------------------------------- #

import numpy
import pandas

# --------------------------------------------------------------------------------------------- #

from bitarray import bitarray

# --------------------------------------------------------------------------------------------- #

from ..file import File
from ..utils import EConst
from ..supported_types import SupportedTypes

# --------------------------------------------------------------------------------------------- #

from .. import utils as ut

# --------------------------------------------------------------------------------------------- #

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------------- #


class SpecEnc():
    """ Specialized Encoder """

    # ----------------------------------------------------------------------------------------- #

    def encode(self, value):
        """ Encodes the Entity object """

        # 1. ...
        encoded = None
        if self.is_encode(value):

            # 1.1 Bitarray...
            if isinstance(value, bitarray):
                encoded = self._encode_bitarray(value)

            # 1.2 DataFrames...
            elif isinstance(value, pandas.DataFrame):
                encoded = self._encode_dataframe(value)

            # 1.3 File...
            elif isinstance(value, File):
                encoded = self._encode_file(value)

            # 1.4 Numpy...
            elif isinstance(value, numpy.ndarray):
                encoded = self._encode_ndarray(value)

            # 1.5 UUID...
            elif isinstance(value, UUID):
                encoded = self._encode_uuid(value)

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

            # 1.1 Bitarray...
            if _type == SupportedTypes.BITARRAY.value:
                decoded = self._decode_bitarray(value)

            # 1.2 Dataframe...
            elif _type == SupportedTypes.DATAFRAME.value:
                decoded = self._decode_dataframe(value)

            # 1.3 File...
            elif _type == SupportedTypes.FILE.value:
                decoded = self._decode_file(value)

            # 1.4 Numpy...
            elif _type == SupportedTypes.NDARRAY.value:
                decoded = self._decode_ndarray(value)

            # 1.5 UUID...
            elif _type == SupportedTypes.UUID.value:
                decoded = self._decode_uuid(value)

        # 3. ...
        return decoded

    # ----------------------------------------------------------------------------------------- #

    def is_encode(self, value):
        """ 
            Checks if Specialized Types:
            - `bitarray.bitarray`, `numpy.ndarray`, `pandas.DataFrame`, `pyon.File`, `uuid.UUID`
        """

        # 1. ...
        return isinstance(
            value,
            (
                bitarray,
                numpy.ndarray,
                pandas.DataFrame,
                File,
                UUID
            )
        )

    # ----------------------------------------------------------------------------------------- #

    def is_decode(self, value):
        """ 
            Checks if Specialized Types:
            - `bitarray.bitarray`, `numpy.ndarray`, `pandas.DataFrame`, `pyon.File`, `uuid.UUID`
        """

        # 1. ...
        is_decode = False

        # 2. ...
        if ut.is_decode_able(value):
            _type = value.get(EConst.TYPE)

            # 1.1 Checks...
            if _type in (
                SupportedTypes.BITARRAY.value,
                SupportedTypes.DATAFRAME.value,
                SupportedTypes.FILE.value,
                SupportedTypes.NDARRAY.value,
                SupportedTypes.UUID.value,
            ):

                # 2.1 ...
                is_decode = True

        # 3. ...
        return is_decode

    # ----------------------------------------------------------------------------------------- #

    def _encode_bitarray(self, value: bitarray):
        """ Encodes a bitarray object to a dictionary representation. """

        # 1. Checks input...
        encoded = None
        if (value is not None) and isinstance(value, bitarray):

            # 1.1 Encodes...
            encoded = {
                EConst.TYPE: SupportedTypes.BITARRAY.value,
                EConst.DATA: value.to01()
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: bitarray. Received: %s", type(value))

        # 3. Returns...
        return encoded

    # ----------------------------------------------------------------------------------------- #

    def _decode_bitarray(self, value: dict):
        """ Decodes a dictionary representation back to a bitarray object. """

        # 1. ...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 ...
            output = bitarray(value[EConst.DATA])

        # 2. ...
        else:

            # 1.1 ...
            logger.error(
                "Invalid bitarray input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. ...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_dataframe(self, value: pandas.DataFrame):
        """ Encodes the DataFrame. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, pandas.DataFrame):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.DATAFRAME.value,
                EConst.DATA: value.to_dict(orient="records"),
                EConst.AUX1: list(value.columns),
                EConst.AUX2: list(value.index),
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: pandas.DataFrame. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_dataframe(self, value: dict):
        """ Decodes to a DataFrame. """

        # 1. Checks input...
        output = None
        if (
            (value is not None)
            and isinstance(value, dict)
            and (EConst.DATA in value)
            and (EConst.AUX1 in value)
            and (EConst.AUX2 in value)
        ):

            # 1.1 Decodes...
            df = pandas.DataFrame(value[EConst.DATA])
            df = df.reindex(columns=value[EConst.AUX1])
            df.index = value[EConst.AUX2]
            output = df

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid dataframe input. Expected: dict with %s, %s, %s. Received: %s",
                EConst.DATA,
                EConst.AUX1,
                EConst.AUX2,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_file(self, value: File):
        """ Encodes the file """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, File):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.FILE.value,
                EConst.DATA: value.to_dict()
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: File. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_file(self, value: dict):
        """ Decodes to File """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = File.from_dict(value[EConst.DATA])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid file input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_ndarray(self, value: numpy.ndarray):
        """ Encodes the Numpy ndarray """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, numpy.ndarray):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.NDARRAY.value,
                EConst.AUX1: value.shape,
                EConst.DATA: value.tolist(),
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: numpy.ndarray. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_ndarray(self, value: dict):
        """ Decodes to Numpy ndarray """

        # 1. Checks input...
        output = None
        if (
            (value is not None)
            and isinstance(value, dict)
            and (EConst.DATA in value)
            and (EConst.AUX1 in value)
        ):

            # 1.1 Decodes...
            np_array = numpy.array(value[EConst.DATA])
            output = np_array.reshape(value[EConst.AUX1])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid ndarray input. Expected: dict with %s and %s. Received: %s",
                EConst.DATA,
                EConst.AUX1,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _encode_uuid(self, value: UUID):
        """ Encodes a UUID object to a string representation. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, UUID):

            # 1.1 Encodes...
            output = {
                EConst.TYPE: SupportedTypes.UUID.value,
                EConst.DATA: str(value)
            }

        # 2. Logs if invalid...
        else:
            logger.error("Invalid input. Expected: UUID. Received: %s", type(value))

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #

    def _decode_uuid(self, value: dict):
        """ Decodes a string representation back to a UUID object. """

        # 1. Checks input...
        output = None
        if (value is not None) and isinstance(value, dict) and (EConst.DATA in value):

            # 1.1 Decodes...
            output = UUID(value[EConst.DATA])

        # 2. If invalid...
        else:

            # 1.1 Logs...
            logger.error(
                "Invalid UUID input. Expected: dict with %s. Received: %s",
                EConst.DATA,
                type(value),
            )

        # 3. Returns...
        return output

    # ----------------------------------------------------------------------------------------- #


# --------------------------------------------------------------------------------------------- #
