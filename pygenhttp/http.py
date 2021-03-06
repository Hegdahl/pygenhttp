'''
HTTP parsing
'''
from typing import Tuple, Dict, Generator, Any
from datetime import date
import platform
from .loop import Loop
from .network import Connection
from . import __version__

STATUS_CODES = {
    200: 'OK',
    400: 'Bad Request',
    404: 'Not Found',
    408: 'Request Timeout',
}

def parse_from_conn(
        connection: Connection
    ) -> Generator[None, None, Tuple[Dict[str, str], Generator[bytes, None, None]]]:
    '''Parse http-headers from a Connection object.
    Returns headers and a generator yielding the request body.'''
    req_line = yield from connection.read_line()
    method, path, http_version = req_line.decode().split(' ')
    headers = {
        'method': method,
        'path': path,
        'http_version': http_version,
    }
    while not Loop.ACTIVE.closing:
        line = (yield from connection.read_line()).strip()
        if not line:
            break
        name, value = line.split(b': ', 1)
        headers[name.decode().lower()] = value.decode()
    return headers, None

def respond_to_conn(connection: Connection, status: int, headers: Dict[str, str], content: bytes) -> None:
    yield
    resp_str = f'HTTP/1.1 {status} {STATUS_CODES.get(status)}'
    headers = {
        'Date': date.today(),
        'Server': f'pygenhttp/{__version__} ({platform.platform()})',
        'Content-Type': 'text/plain',
        'Connection': 'close',
        **headers
    }
    if content is not None:
        headers['Content-Length'] = len(content)
    header_str = '\r\n'.join(f'{name}: {value}' for name, value in headers.items())
    resp = b'\r\n'.join((
        resp_str.encode(),
        header_str.encode(),
        b'',
    ))
    connection.send(
        resp if content is None else b'\r\n'.join((
            resp,
            content,
            b'',
        ))
    )
    if headers['Connection'] == 'close':
        connection.close()
