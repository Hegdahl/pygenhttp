'''
Class containing a loop that serves http requests.
'''
from typing import Callable
import re
from .loop import Loop
from .network import listen_tcp
from .http import parse_from_conn, respond_to_conn, STATUS_CODES
from .pages import PAGES
from .response import Response

def make_default_error(status_code):
    def default_error(*_):
        return (yield from Response.HTML(PAGES[status_code], status=status_code))
    return default_error

class Server:
    _match_all = re.compile(r'\.*')

    def __init__(self, routes=()):
        self.routes = list(routes)
        self.error_handlers = {
            status_code: make_default_error(status_code)
            for status_code in STATUS_CODES
        }

    def route(self, pattern: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            self.routes.append((re.compile(f'^{pattern}$'), func))
            return func
        return decorator

    def _handle_connection(self, conn):
        try:
            headers, body_gen = yield from parse_from_conn(conn)
            path = headers['path']
            for pattern, func in self.routes:
                match = pattern.match(path[1:])
                if match:
                    status, headers, body = yield from func(
                        headers,
                        body_gen,
                        **match.groupdict())
                    try:
                        yield from body_gen
                    except (TypeError, GeneratorExit):
                        pass
                    yield from respond_to_conn(conn, status, headers, body)
                    return
            yield from respond_to_conn(conn, *(
                yield from self.error_handlers[404]()))
            return
        except TimeoutError:
            yield from respond_to_conn(conn, *(
                yield from self.error_handlers[408]()))
        except (TypeError, IndexError, KeyError, UnicodeDecodeError):
            yield from respond_to_conn(conn, *(
                yield from self.error_handlers[400]()))

    def serve(self, host: str = '0.0.0.0', port: int = 8080) -> None:
        loop = Loop()
        loop.enqueue(listen_tcp(host, port, self._handle_connection))
        loop.start()
