import socket
import os
import time
HOST = 'localhost'
PORT = 30552
start_time = time.time()
quality = 0

class tcp_sender:
    def update_quality(self):
        global quality, start_time
        rtt = time.time() - start_time
        rescale_rtt = rtt * 1000 - 500
        if rescale_rtt > 18:
            quality = max(0, quality - 1)
        elif rescale_rtt < 12:
            quality = min(4, quality + 1)
        print(f"Received ACK from receiver. Calling my_function...{(quality, rescale_rtt)}")


    def send_picture(self, name, socket):
        with open(name, 'rb') as f:
            data = f.read()
        socket.sendall(data + b"<end>")
        print(f'Sent {len(data)} bytes of data for {name}')
        # print(data[:500])


    def send_chunk(self, quality, s, start, end):
        for i in range(start, end):
            name = f'{quality}/{i}.png'
            if os.path.isfile(name):
                self.send_picture(name, s)

    def run(self):
        global start_time
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #s.connect((HOST, PORT))
            s.bind((HOST, PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                print(addr)
                quality_names = ['240p', '360p', '480p', '720p', '1080p']
                for i in range(1, 21, 2):
                    start_time = time.time()
                    self.send_chunk(quality_names[quality], conn, i, i + 2)
                    time.sleep(0.5)
                    while True:
                        ack = conn.recv(1024)
                        if ack:
                            if "ACK" in ack.decode():
                                self.update_quality()
                                break
                            else:
                                print(ack)
                time.sleep(0.5)
                conn.close()

t = tcp_sender()
t.run()