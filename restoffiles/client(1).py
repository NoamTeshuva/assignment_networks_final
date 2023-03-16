import socket
import time
import random

# create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# define the server address and port
server_address = ('localhost', 5005)

# receive the video data from the server
f = open('video.mp4', 'wb')
while True:
    client_socket.sendto(str(random.randint(500, 4096)).encode('utf-8'), server_address)

    data, server_address = client_socket.recvfrom(2048)
    f.write(data)

    print(data)
    if not data:
        break
