'''
Concurrent networking tools.
'''
from typing import Generator
from collections import deque
import socket
from .loop import Loop, schedule

class Connection:
    '''
    Socket wrapper for use in Loop
    '''
    def __init__(self, sock: socket.socket, chunk_size=2**18):
        sock.settimeout(0)
        self._sock = sock
        self.chunk_size = chunk_size
        self._recv_buffer = b''
        self._send_buffer = deque()
        self._closing = False
        Loop.ACTIVE.enqueue(self._loop())

    def _loop(self):
        while not self._closing:
            yield
            try:
                self._recv_buffer += self._sock.recv(self.chunk_size)
            except BlockingIOError:
                pass
            if self._send_buffer:
                self._sock.send(self._send_buffer.popleft())

    def read_all(self) -> bytes:
        '''Read the entire buffer.'''
        buffer = self._recv_buffer
        self._recv_buffer = b''
        return buffer

    def read_up_to(self, byte_count) -> bytes:
        '''Read up to byte_count bytes from the buffer.'''
        chunk = self._recv_buffer[:byte_count]
        self._recv_buffer = self._recv_buffer[byte_count:]
        return chunk

    def read_between(self,
                     min_byte_count: int,
                     max_byte_count: int) -> Generator[None, None, bytes]:
        '''Get bytes from the buffer.'''
        while len(self._recv_buffer) < min_byte_count:
            yield
        chunk = self._recv_buffer[:max_byte_count]
        self._recv_buffer = self._recv_buffer[max_byte_count:]
        return chunk

    def read(self, byte_count) -> Generator[None, None, bytes]:
        '''Read up to byte_count bytes from the buffer,
        but at least 1.'''
        return self.read_between(1, byte_count)

    def read_exactly(self, byte_count: int) -> Generator[None, None, bytes]:
        '''Read exactly to byte_count bytes from the buffer.'''
        return self.read_between(byte_count, byte_count)

    def yield_read(self, byte_count) -> Generator[bytes, None, None]:
        '''Yield byte chunks until byte_count bytes have been yielded.'''
        idx = 0
        while idx < byte_count:
            chunk = self.read_up_to(byte_count-idx)
            yield chunk
            idx += len(chunk)

    def read_until(self, delimiter: bytes) -> Generator[None, None, bytes]:
        '''Read from the buffer until a delimiter.
        Resulting bytes do not contain the delimiter.'''
        while delimiter not in self._recv_buffer:
            yield
        chunk, self._recv_buffer = self._recv_buffer.split(delimiter, 1)
        return chunk

    def read_line(self) -> Generator[None, None, bytes]:
        '''Read from buffer until a newline'''
        return self.read_until(b'\n')

    def send(self, data: bytes) -> None:
        '''Add data to send buffer split into chunk
        with a maximum size of chunk_size.'''
        for i in range(0, round(len(data)/self.chunk_size+.5)):
            self._send_buffer.append(data[i*self.chunk_size:(i+1)*self.chunk_size])

    def close(self):
        '''Close connection gracefully.'''
        self._closing = True
        yield
        self._sock.close()

    def __del__(self):
        tuple(self.close())

    def __str__(self):
        phost, pport = self._sock.getpeername()
        shost, sport = self._sock.getsockname()
        return f'Connection({shost}:{sport} <- {phost}:{pport})'

def listen_tcp(host: str, port: int, connect_cb) -> None:
    '''
    Listen for connections on host:port and call a callback
    when recieving connection with connection object.
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0)
        sock.bind((host, port))
        sock.listen()
        while True:
            yield
            try:
                csock, _ = sock.accept()
            except BlockingIOError:
                continue
            conn = Connection(csock)
            Loop.ACTIVE.enqueue(schedule(
                connect_cb(conn),
                conn.close,
            ))