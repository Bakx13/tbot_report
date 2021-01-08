# при разработке

import os

DEBUG = True

TITLE = 'SpecialistOff.NET'

DIR_BASE = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1])
DIR_DATA = DIR_BASE + '/data'
DIR_FILES = DIR_DATA + '/files'

MIMETYPES = {
    'gif': 'image/gif',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'txt': 'text/plain'
}

SERVERS = [
    {'name': 'server1', 'IP': '8.8.8.8', 'port': '80'}
]