# --------------------------------------------------------------------------------------------- #
""" Pyon: Python Object Notation - Supported Types """
# --------------------------------------------------------------------------------------------- #

from enum import Enum

# --------------------------------------------------------------------------------------------- #


class SupportedTypes(Enum):
    """ PyonEncoder Supported Types """

    # ----------------------------------------------------------------------------------------- #

    BITARRAY = "bitarray"
    BYTEARRAY = "bytearray"
    BYTES = "bytes"
    BOOL = "bool"
    CHAINMAP = "chainmap"
    CLASS = "class"
    COMPLEX = "complex"
    COUNTER = "counter"
    DATACLASS = "dataclass"
    DATAFRAME = "dataframe"
    DATE = "date"
    DATETIME = "datetime"
    DECIMAL = "decimal"
    DEFAULTDICT = "defaultdict"
    DEQUE = "deque"
    DICT = "dict"
    ENUM = "enum"
    FILE = "file"
    FLAG = "flag"
    FLOAT = "float"
    FROZENSET = "frozenset"
    INT = "int"
    INTENUM = "intenum"
    LIST = "list"
    NAMEDTUPLE = "namedtuple"
    NDARRAY = "ndarray"
    NONE = "none"
    SET = "set"
    STR = "str"
    TIME = "time"
    TUPLE = "tuple"
    UUID = "uuid"

    # ----------------------------------------------------------------------------------------- #


# --------------------------------------------------------------------------------------------- #
