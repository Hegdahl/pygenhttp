'''
Default html page loading
'''
import os
import platform
from . import __version__
from .http import STATUS_CODES

DIRNAME = os.path.realpath(os.path.dirname(__file__))
PAGES_DIR = os.path.join(DIRNAME, 'pages')
PAGES = {}
for filename in os.listdir(PAGES_DIR):
    with open(os.path.join(PAGES_DIR, filename), 'rb') as file:
        PAGES[filename.rpartition('.')[0]] = file.read()

for status_code, status_name in STATUS_CODES.items():
    PAGES[status_code] = PAGES['error'].decode().format(
        status_code=status_code,
        status_name=status_name,
        version=__version__,
        platform=platform.platform(),
    ).encode()
