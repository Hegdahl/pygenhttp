'''
Default html page loading
'''
import os
DIRNAME = os.path.realpath(os.path.dirname(__file__))
PAGES_DIR = os.path.join(DIRNAME, 'pages')
PAGES = {}
for filename in os.listdir(PAGES_DIR):
    with open(os.path.join(PAGES_DIR, filename), 'rb') as file:
        PAGES[filename.rpartition('.')[0]] = file.read()
