from pygenhttp import Server
from pygenhttp.response import Response

s = Server()

@s.route('')
def index(*_):
    return (yield from Response.Text('working.'))

s.serve()
