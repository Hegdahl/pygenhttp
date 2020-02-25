from pygenhttp import Server
from pygenhttp.response import Response

server = Server()
@server.route('')
def index(*_):
    return (yield from Response.Text('working.'))

server.serve()
