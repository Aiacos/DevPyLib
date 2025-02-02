__author__ = 'Lorenzo Argentieri'

import inspect


def get_docs(element, advanced=True):
    """Get the documentation string from a given element.

    Args:
        element: The object to extract the documentation from.
        advanced: A boolean indicating whether to return the full documentation
            string or a shorter version.

    Returns:
        The documentation string for the given element.
    """
    if advanced:
        return inspect.getdoc(element)
    else:
        return element.__doc__


if __name__ == "__main__":
    print(get_docs(get_docs))