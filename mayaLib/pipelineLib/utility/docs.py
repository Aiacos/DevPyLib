__author__ = 'Lorenzo Argentieri'

import inspect


def getDocs(element, advanced=True):
    """
    Get Docs from a Function
    :param element:
    :param advanced:
    :return:
    """
    if advanced:
        docs = inspect.getdoc(element)
        return docs
        print 'advanced'
    else:
        print element.__doc__
        print help(element)
        print 'base'


if __name__ == "__main__":
    print getDocs(getDocs)
