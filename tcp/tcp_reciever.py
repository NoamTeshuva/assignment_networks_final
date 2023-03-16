import socket
import os

HOST = 'localhost'
PORT = 20510

def save_data_to_file(data, index):
    with open(f'output/received_data_{index}.png', 'wb') as f:
        f.write(data)

class tcp_reciever:
    def __init__(self, addr):
            self.port = addr[1]

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.connect((HOST, self.port))
            # s.listen()
            with s:
               # print('Connected by', addr)
                index = 1
                chunks = []
                while True:
                    data = s.recv(65536)
                    if not data:
                        break
                    print(f'Received {len(data)} bytes of data for received_data_{index}')
                    # print(b"<end>" in data)
                    if b"<end>" in data:
                        list = data.split(b"<end>")
                        chunks.append(list[0])
                        data = b''.join(chunks)
                        save_data_to_file(data, index)
                        chunks = [list[1]]
                        index += 1
                        s.sendall(b"ACK")
                    else:
                        chunks.append(data)
# t = tcp_reciever()
# t.run()