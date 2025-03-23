# --------------------------------------------------------------------------------------------- #
""" Pyon: Python Object Notation - Utils """
# --------------------------------------------------------------------------------------------- #

import importlib

# --------------------------------------------------------------------------------------------- #


class EConst:
    """ Constants used for encoding e decoding data in pyon source. """

    AUX1 = "__aux1__"
    AUX2 = "__aux2__"
    CLASS = "__class__"
    DATA = "__data__"
    DICT = "__dict__"
    TYPE = "__type__"
    FIELDS = "_fields"


# --------------------------------------------------------------------------------------------- #


def is_decode_able(value):
    """ Checks if `value` can be decoded. """

    # 1. ...
    return isinstance(value, dict) and (EConst.TYPE in value)


# --------------------------------------------------------------------------------------------- #


def get_class_name(obj):
    """
    Retrieve the fully qualified class name of an object or class.

    Args:
        obj: The object or class to inspect.

    Returns:
        str: A string representing the fully qualified class name, including the module name.
    """

    # 1. ...
    module, name = None, None

    # 2. ...
    if isinstance(obj, type):
        module, name = f"{obj.__module__}", f"{obj.__qualname__}"

    # 3. ...
    else:
        module, name = f"{obj.__class__.__module__}", f"{obj.__class__.__name__}"

    # 4. ...
    return f"{module}.{name}"


# --------------------------------------------------------------------------------------------- #


def get_class(obj):
    """
    Retrieve the class object referenced by a serialized representation.

    Args:
        obj: A dictionary containing serialized class metadata, including the class name.

    Returns:
        type or None: The class object if it exists and can be imported; otherwise, None.
    """

    # 1. ...
    cls = None
    if isinstance(obj, dict) and (EConst.CLASS in obj):

        # 1.1 ...
        class_name = obj[EConst.CLASS]
        if "." in class_name:

            # 2.1 ...
            try:

                # 3.1 ...
                module_name, class_name = class_name.rsplit(".", 1)
                module = importlib.import_module(module_name)

                # 3.2 ...
                cls = getattr(module, class_name)

            # 2.2 ...
            except (ModuleNotFoundError, AttributeError):
                cls = None

    # 2. ...
    return cls


# --------------------------------------------------------------------------------------------- #
