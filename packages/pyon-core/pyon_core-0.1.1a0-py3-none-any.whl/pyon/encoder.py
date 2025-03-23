""" Pyon: Python Object Notation - Encoder """
# --------------------------------------------------------------------------------------------- #

from .encoders import BaseEnc, ColEnc, DateEnc, SpecEnc, NumEnc, MapEnc

# --------------------------------------------------------------------------------------------- #

from . import utils as ut

# --------------------------------------------------------------------------------------------- #


class PyonEncoder():
    """ Pyon Encoder """

    # ----------------------------------------------------------------------------------------- #

    def __init__(self):
        """ Initializes a Pyon Encoder """

        # 1. ...
        self.base_enc = BaseEnc()
        self.date_enc = DateEnc()
        self.spec_enc = SpecEnc()
        self.num_enc = NumEnc()

        # 2. ...
        self.col_enc = ColEnc(self)
        self.map_enc = MapEnc(self)

    # ----------------------------------------------------------------------------------------- #

    def encode(self, value):
        """ Encodes the Entity object """

        # 1. ...
        encoded = None
        if value is not None:

            # 1.1 Base Types...
            if self.base_enc.is_encode(value):
                encoded = self.base_enc.encode(value)

            # 1.2 Numeric Types...
            elif self.num_enc.is_encode(value):
                encoded = self.num_enc.encode(value)

            # 1.3 Collection Types...
            elif self.col_enc.is_encode(value):
                encoded = self.col_enc.encode(value)

            # 1.4 Datetime Types...
            elif self.date_enc.is_encode(value):
                encoded = self.date_enc.encode(value)

            # 1.5 Specialized Types...
            elif self.spec_enc.is_encode(value):
                encoded = self.spec_enc.encode(value)

            # 1.6 Mapping Types...
            elif self.map_enc.is_encode(value):
                encoded = self.map_enc.encode(value)

        # 2. ...
        return encoded

    # ----------------------------------------------------------------------------------------- #

    def decode(self, value):
        """ Decodes the value """

        # 1. ...
        decoded = None
        if ut.is_decode_able(value):

            # 1.1 Numeric Types...
            if self.num_enc.is_decode(value):
                decoded = self.num_enc.decode(value)

            # 1.2 Collection Types...
            elif self.col_enc.is_decode(value):
                decoded = self.col_enc.decode(value)

            # 1.3 Datetime Types...
            elif self.date_enc.is_decode(value):
                decoded = self.date_enc.decode(value)

            # 1.4 Specialized Types...
            elif self.spec_enc.is_decode(value):
                decoded = self.spec_enc.decode(value)

            # 1.5 Mapping Types...
            elif self.map_enc.is_decode(value):
                decoded = self.map_enc.decode(value)

        # 2. Base Types...
        elif self.base_enc.is_decode(value):
            decoded = self.base_enc.decode(value)

        # 3. ...
        return decoded

    # ----------------------------------------------------------------------------------------- #


# --------------------------------------------------------------------------------------------- #
