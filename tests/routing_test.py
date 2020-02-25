from pygenhttp import Server
from pygenhttp.response import Response

server = Server()

@server.route('')
def index(*_):
    return (yield from Response.HTML('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Test Page</title>
            </head>
            <body>
                <h1>This is a test page.</h1>
                <p>If you can read this, it's probably working as it should.</p>
            </body>
        </html>
    '''))

@server.route(r'regex_test/(?P<path_match>\w*)')
def regex_test(headers, _, path_match):
    return (yield from Response.HTML(f'''
        <!DOCTYPE html>
        <html>
          <head>
            <title>Route test</title>
          </head>
          <body>
            <p>The named capture was {path_match!r}.</p>
          </body>
        </html>
    '''))

@server.route('json_test')
def json_test(headers, _):
    return (yield from Response.JSON({
        'request-headers': headers,
        'other': 'stuff',
    }))

@server.route('redir')
def redir_test(*_):
    return (yield from Response.Redirect('/regex_test/you_were_redirected'))

if __name__ == "__main__":
    server.serve()
