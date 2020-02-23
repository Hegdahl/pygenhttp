'''
Test functionality of pygenhttp.loop.Loop.
'''
from pygenhttp.loop import Loop, call_later
from pygenhttp.network import listen_tcp

def main():
    '''
    Main part of test
    '''
    def client_connected(conn):
        print(conn)
        while True:
            line = (yield from conn.read_line()).strip()
            print(line)
            if not line:
                break
        conn.send(b'Hello!\r\n')
    loop = Loop()
    loop.enqueue(call_later(2, print, 'a'))
    loop.enqueue(call_later(1, print, 'b'))
    loop.enqueue(call_later(3, print, 'c'))
    loop.enqueue(listen_tcp('', 8080, client_connected))
    loop.start()

if __name__ == "__main__":
    main()
