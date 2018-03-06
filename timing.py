from __future__ import print_function
import logging, time
from inspect import getcallargs, getargspec
from collections import OrderedDict, Iterable
from itertools import *
from functools import wraps

# timelogger = logging.getLogger('timelog.timing')
# logger = logging.getLogger('timelog.auxiliary')
# logger.setLevel(logging.INFO)
# # create file handler which logs even debug messages
# fh = logging.FileHandler('timelog.log')
# fh.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
# # add the handlers to the logger
# logger.addHandler(fh)

# logging.basicConfig(filename='timelog.log',
#                     level=logging.INFO,
#                     format='%(asctime)s | %(filename)s | %(message)s')

def timelog(logger):

    def decorator(funcName):
        def wrapper(*args, **kwargs):
            print(args, kwargs)
            print(funcName)
            print(funcName.__name__)

            t1 = time.time()
            value = funcName(*args, **kwargs)
            t2 = time.time()

            logger.info(funcName.__name__
                         + str(args) + ", " + str(kwargs)
                         + " | " + str(t2-t1))

            return value

        wrapper.__name__ = funcName.__name__
        return wrapper
    return decorator

