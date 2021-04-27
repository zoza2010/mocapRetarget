'''
useful utils
'''
from default_configs import *


def expand_path(path):
    import os
    '''
    expans path to absolute from relative
    '''
    resolved_path = path
    if not os.path.isabs(path):
        resolved_path = os.path.join(APP_ROOT, path).replace('\\', '/')
    return resolved_path