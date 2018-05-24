"""
name @ utils

Utilities to work with names and strings
"""


def removeSuffix(name):
    """
    Remove suffix from given name string
    
    @param name: given name string to process
    @return: str, name without suffix
    """

    edits = name.split('_')

    if len(edits) < 2:
        return name

    suffix = '_' + edits[-1]
    nameNoSuffix = name[:-len(suffix)]

    return nameNoSuffix

def getSide(name):
    edits = name.split('_')
    if len(edits) < 3:
        return ''

    side = edits[0] + '_'
    return side

def getAlpha(i):
    if i >= 0 and i <= 25:
        return chr(65 + i)
    return ''
