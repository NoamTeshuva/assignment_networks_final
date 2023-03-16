import socket

HOST = 'localhost'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to connect to (same as the receiver)

def send_picture(name, socket):
    with open(name, 'rb') as f:
        data = f.read()
    # message = b'A' * 65536  # Create a byte string of 65536 bytes
    socket.sendall(data)
    print('Sent', len(data), 'bytes of data')


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    send_picture('1.png', s)



