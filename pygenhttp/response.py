'''
Response object with various constructors.
'''
import json

class Response:
    '''Class that can be unpacked to status, headers and body_gen'''

    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body
    
    def __iter__(self):
        return iter((self.status, self.headers, self.body))

    @classmethod
    def Bytes(cls, data, status=200, headers=None):
        yield
        return cls(
            status,
            {'Content-Type': 'application/octet-stream', **(headers or {})},
            data,
        )

    @classmethod
    def Text(cls, text, status=200, headers=None):
        yield
        return cls(
            status,
            {'Content-Type': 'text/plain', **(headers or {})},
            text.encode(),
        )

    @classmethod
    def HTML(cls, doc, status=200, headers=None):
        yield
        return cls(
            status,
            {'Content-Type': 'text/html', **(headers or {})},
            doc if isinstance(doc, bytes) else doc.encode(),
        )

    @classmethod
    def JSON(cls, obj, status=200, headers=None):
        yield
        return cls(
            status,
            {'Content-Type': 'application/json', **(headers or {})},
            json.dumps(obj).encode(),
        )

    @classmethod
    def Redirect(cls, path, status=307, headers=None):
        yield
        return cls(
            status,
            {'Location': path},
            b'',
        )
