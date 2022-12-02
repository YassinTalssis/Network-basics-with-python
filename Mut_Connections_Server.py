# multiconn-server.py


import socket
import selectors
import types

sel = selectors.DefaultSelector()
host = "127.0.0.1"  # The server's hostname or IP address
port = 6666  # The port used by the server

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)#to configure the socket in non-blocking mode
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ: #if the socket is ready for reading
        recv_data = sock.recv(1024) 
        if recv_data:
            data.outb += recv_data #Add received data to data that we'll send it later
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
#sockets are no  blocked
lsock.setblocking(False)
#registers the socket to be monitored with sel.select()
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        #sel.select returns a list of tuples, one for each socket. Each tuple contains a key and a mask.
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:#data conatin what's send and receive
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
