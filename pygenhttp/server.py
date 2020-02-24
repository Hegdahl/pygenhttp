'''
Class containing a loop that serves http requests.
'''
from typing import Callable
import re
from .loop import Loop
from .network import listen_tcp
from .http import parse_from_conn, respond_to_conn
from .pages import PAGES
from .response import Response

def default_not_found(*_):
    yield
    return Response.HTML(PAGES['404'], status=404)

class Server:
    _match_all = re.compile(r'\.*')

    def __init__(self, routes=()):
        self.routes = list(routes)
        self.not_found = default_not_found

    def route(self, pattern: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            self.routes.append((re.compile(f'^{pattern}$'), func))
            return func
        return decorator

    def _handle_connection(self, conn):
        headers, body_gen = yield from parse_from_conn(conn)
        path = headers['path']
        print(f'[{conn}]: {headers["method"]} {path}')
        for pattern, func in self.routes + [(self._match_all, self.not_found)]:
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
                respond_to_conn(conn, status, headers, body)
                return

    def serve(self, host: str = '0.0.0.0', port: int = 8080) -> None:
        loop = Loop()
        loop.enqueue(listen_tcp(host, port, self._handle_connection))
        loop.start()
