from pygenhttp import Server

s = Server()

@s.route('')
def intentional_bad_request(*_):
    raise TypeError

s.serve()
