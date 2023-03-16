import socket

HOST = 'localhost'
PORT = 65432

def save_data_to_file(data):
    with open(f'received_data_{2}.jpg', 'wb') as f:
        f.write(data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        data = conn.recv(65536)
        save_data_to_file(data)
        print('Received', len(data), 'bytes of data')




