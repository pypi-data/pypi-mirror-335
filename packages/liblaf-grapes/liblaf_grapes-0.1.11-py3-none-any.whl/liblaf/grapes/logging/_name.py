def full_qual_name(obj: object) -> str:
    """Returns the fully qualified name of an object, including its module and class.

    Args:
        obj: The object for which to get the fully qualified name.

    Returns:
        The fully qualified name of the object, including its module and class. If the object is callable, "()" is appended to the name.
    """
    name: str = obj.__module__ + "." + obj.__qualname__
    if callable(obj):
        name += "()"
    return name
