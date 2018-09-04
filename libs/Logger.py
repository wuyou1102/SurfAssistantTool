# -*- encoding:UTF-8 -*-
import logging.config
import os
import sys
from time import time, localtime, strftime

__LOG = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "Logs")
if not os.path.exists(__LOG):
    os.makedirs(__LOG)

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'delay': True,
            'filename': os.path.join(__LOG, '%s.log' % strftime("%Y_%m_%d-%H_%M_%S", localtime(time()))),
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
    }
})
