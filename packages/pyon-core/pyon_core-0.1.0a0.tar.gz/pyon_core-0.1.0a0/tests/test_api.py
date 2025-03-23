# --------------------------------------------------------------------------------------------- #
""" Tests for Pyon: Encode and Decode """
# --------------------------------------------------------------------------------------------- #

from collections import ChainMap, Counter, deque, defaultdict, namedtuple
from dataclasses import dataclass
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

# --------------------------------------------------------------------------------------------- #

from bitarray import bitarray

# --------------------------------------------------------------------------------------------- #

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------------------------- #

import pytest
import pyon

# --------------------------------------------------------------------------------------------- #

from pyon import File

# --------------------------------------------------------------------------------------------- #


# Test Enums
class Color(Enum):
    """ For Enum Test """
    RED = 1
    GREEN = 2
    BLUE = 3


# --------------------------------------------------------------------------------------------- #


# Test Dataclasses
@dataclass
class Person:
    """ For Dataclass Test """
    name: str
    age: int


# --------------------------------------------------------------------------------------------- #


# Test Class
class Cat:
    """ For Dataclass Test """
    name: str
    age: int
    def __init__(self, name, age):
        self.name = name
        self.age = age


# --------------------------------------------------------------------------------------------- #


# Namedtuple for Tests
Named = namedtuple("Named", ["field1", "field2"])


# --------------------------------------------------------------------------------------------- #


class TestPyonEncodeDecode:
    """ Test suite for Pyon's encode and decode functions """

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [bitarray("1101"), None, "invalid", 10, 3.14])

    def test_bitarray(self, value):
        """ Test encoding and decoding for bitarray. """

        # 1. Default test...
        self._test_default(value, bytearray)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [bytearray(b"hello"), None, "invalid", 10, 3.14])

    def test_bytearray(self, value):
        """ Test encoding and decoding for bytearray. """

        # 1. Default test...
        self._test_default(value, bytearray)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [b"hello", None, "invalid", 10, 3.14])

    def test_bytes(self, value):
        """ Test encoding and decoding for bytes. """

        # 1. Default test...
        self._test_default(value, bytes)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [True, False, None, "invalid", 3.14])

    def test_bool(self, value):
        """ Test encoding and decoding for boolean values. """

        # 1. Default test...
        self._test_default(value, bool)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [ChainMap({"a": 1}, {"b": 2}), None, "invalid", 10, 3.14])

    def test_chainmap(self, value):
        """ Test encoding and decoding for ChainMap. """

        # 1. Default test...
        self._test_default(value, ChainMap)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [Cat("Malbec", 6), None, "invalid", 10, 3.14])

    def test_class(self, value):
        """ Test encoding and decoding for Class. """

        # 1. Default test...
        self._test_default(value, Cat)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [2 + 3j, None, "invalid", 10, 3.14])

    def test_complex(self, value):
        """ Test encoding and decoding for complex numbers. """

        # 1. Default test...
        self._test_default(value, complex)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [Counter({"a": 1, "b": 2}), None, "invalid", 10, 3.14])

    def test_counter(self, value):
        """ Test encoding and decoding for Counter. """

        # 1. Default test...
        self._test_default(value, complex)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [Person("Alice", 25), None, "invalid", 10, 3.14])

    def test_dataclass(self, value):
        """ Test encoding and decoding for dataclass. """

        # 1. Default test...
        self._test_default(value, Person)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [date.today(), None, "invalid", 10, 3.14])

    def test_date(self, value):
        """ Test encoding and decoding for date. """

        # 1. Default test...
        self._test_default(value, date)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [datetime.now(), None, "invalid", 10, 3.14])

    def test_datetime(self, value):
        """ Test encoding and decoding for datetime. """

        # 1. Default test...
        self._test_default(value, datetime)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [Decimal("123.45"), None, "invalid", 10, 3.14])

    def test_decimal(self, value):
        """ Test encoding and decoding for complex numbers. """

        # 1. Default test...
        self._test_default(value, Decimal)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [defaultdict(int, a=1), None, "invalid", 10, 3.14])

    def test_defaultdict(self, value):
        """ Test encoding and decoding for defaultdict. """

        # 1. Default test...
        self._test_default(value, defaultdict)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [deque(["a", "b"]), None, "invalid", 10, 3.14])

    def test_deque(self, value):
        """ Test encoding and decoding for deque. """

        # 1. Default test...
        self._test_default(value, deque)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [Color.RED, None, "invalid", 10, 3.14])

    def test_enum(self, value):
        """ Test encoding and decoding for Enum. """

        # 1. Default test...
        self._test_default(value, Enum)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize(
        "value", [File("./tests/data/img.jpg"), None, "invalid", 10, 3.14]
    )

    def test_file(self, value):
        """ Test encoding and decoding for File. """

        # 1. Default test...
        self._test_default(value, File)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [2.72, None, "invalid", 10, False])

    def test_float(self, value):
        """ Test encoding and decoding for float. """

        # 1. Default test...
        self._test_default(value, float)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [frozenset([1, 2, 3]), None, "invalid", 10, 3.14])

    def test_frozenset(self, value):
        """ Test encoding and decoding for frozenset. """

        # 1. Default test...
        self._test_default(value, frozenset)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [42, None, "invalid", 10, False])

    def test_int(self, value):
        """ Test encoding and decoding for int. """

        # 1. Default test...
        self._test_default(value, int)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [Named("value1", 123), None, "invalid", 10, 3.14])

    def test_namedtuple(self, value):
        """ Test encoding and decoding for namedtuple. """

        # 1. Default test...
        self._test_default(value, Named)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [{1, 2, 3}, None, "invalid", 10, 3.14])

    def test_set(self, value):
        """ Test encoding and decoding for set. """

        # 1. Default test...
        self._test_default(value, set)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", ["Hello World", None, "invalid", 10, 3.14])

    def test_str(self, value):
        """ Test encoding and decoding for str. """

        # 1. Default test...
        self._test_default(value, str)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [time(14, 30, 15), None, "invalid", 10, 3.14])

    def test_time(self, value):
        """ Test encoding and decoding for time. """

        # 1. Default test...
        self._test_default(value, time)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [(1, "two", 3.0), None, "invalid", 10, 3.14])

    def test_tuple(self, value):
        """ Test encoding and decoding for tuple. """

        # 1. Default test...
        self._test_default(value, tuple)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize("value", [uuid4(), None, "invalid", 10, 3.14])

    def test_uuid(self, value):
        """ Test encoding and decoding for uuid. """

        # 1. Default test...
        self._test_default(value, UUID)

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize(
        "value", [np.array([[1, 2, 3], [4, 5, 6]]), None, "invalid", 10, 3.14]
    )

    def test_ndarray(self, value):
        """ Test encoding and decoding for Numpy Array. """

       # 1. Valid case...
        if isinstance(value, np.ndarray):

            # 1.1 Encode, Decode...
            encoded = pyon.encode(value)
            decoded = pyon.decode(encoded)

            # 1.2 Asserts: encoded...
            assert isinstance(encoded, str)

            # 1.3 Asserts: decoded...
            assert np.array_equal(decoded, value)

        # 2. None, Other...
        else:

            # 1.1 Encode, Decode, Asserts...
            decoded = pyon.decode(pyon.encode(value))
            assert decoded == value

    # ----------------------------------------------------------------------------------------- #

    @pytest.mark.parametrize(
        "value",
        [pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]}), None, "invalid", 10, 3.14],
    )

    def test_dataframe(self, value):
        """ Test encoding and decoding for Pandas Dataframe. """

       # 1. Valid case...
        if isinstance(value, pd.DataFrame):

            # 1.1 Encode, Decode...
            encoded = pyon.encode(value)
            decoded = pyon.decode(encoded)

            # 1.2 Asserts: encoded...
            assert isinstance(encoded, str)

            # 1.3 Asserts: decoded...
            assert isinstance(decoded, pd.DataFrame)
            assert decoded.equals(value)

        # 2. None, Other...
        else:

            # 1.1 Encode, Decode, Asserts...
            decoded = pyon.decode(pyon.encode(value))
            assert decoded == value

    # ----------------------------------------------------------------------------------------- #

    def _test_default(self, value, clazz):
        """ Test encoding and decoding for complex numbers. """

        # 1. Valid case...
        if isinstance(clazz, type) and isinstance(value, clazz):

            # 1.1 Encode, Decode...
            encoded = pyon.encode(value)
            decoded = pyon.decode(encoded)

            # 1.2 Asserts: encoded...
            assert encoded != value
            assert isinstance(encoded, str)

            # 1.3 If not builtins, checks name in type...
            if not self._is_builtins(clazz) or isinstance(clazz, dict):
                assert clazz.__name__.lower() in encoded.lower()

            # 1.4 Asserts: decoded...
            if not (hasattr(decoded, "__dict__") and isinstance(decoded.__dict__, dict)):
                assert decoded == value

            # 1.5 Asserts: decode dict...
            elif hasattr(value, "__dict__") and isinstance(value.__dict__, dict):
                for key, val in value.__dict__.items():

                    # 3.1 Both must have the same key and value...
                    assert key in decoded.__dict__
                    assert decoded.__dict__[key] == val

            # 1.6 Fails...
            else:
                pytest.fail(
                    (
                        f"Fail. Expected: {clazz}. "
                        f"Value: {type(value)}. "
                        f"Result: {type(decoded)}."
                    )
                )

        # 2. None, Other...
        else:

            # 1.1 Encode, Decode, Asserts...
            decoded = pyon.decode(pyon.encode(value))
            assert decoded == value

    # ----------------------------------------------------------------------------------------- #

    def _is_builtins(self, clazz):
        """ Checks if a class is builtins """

        # 1. Checks...
        return isinstance(clazz, type) and clazz in {int, float, bool, str}

    # ----------------------------------------------------------------------------------------- #


# --------------------------------------------------------------------------------------------- #
