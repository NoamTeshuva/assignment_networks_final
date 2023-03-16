# import socket
# import time
# import random
#
# # create a UDP socket
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
# # define the server address and port
# server_address = ('localhost', 5005)
#
# # receive the video data from the server
# f = open('video.mp4', 'wb')
# while True:
#     client_socket.sendto(str(random.randint(500, 4096)).encode('utf-8'), server_address)
#
#     data, server_address = client_socket.recvfrom(2048)
#     f.write(data)
#
#     if not data:
#         break
#
# # close the socket and file
# client_socket.close()
# f.close()

# import socket
# import time
# import random
#
# # create a UDP socket
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
# # define the server address and port
# server_address = ('localhost', 5005)
#
# # receive the video data from the server
# f = open('video.mp4', 'wb')
# while True:
#     try:
#         client_socket.sendto(str(random.randint(500, 4096)).encode('utf-8'), server_address)
#
#         data, _ = client_socket.recvfrom(2048)
#         f.write(data)
#
#         if not data:
#             break
#
#     except ConnectionResetError:
#         print("Connection reset error, retrying...")
#         time.sleep(1)
#
# f.close()
# client_socket.close()
# import socket
# import time
# import random
#
# # create a UDP socket
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
# # define the server address and port
# server_address = ('localhost', 5005)
#
# # receive the video data from the server
# f = open('video.mp4', 'wb')
# while True:
#     # send a request to the server for available bandwidth
#     client_socket.sendto(str(random.randint(500, 4096)).encode('utf-8'), server_address)
#
#     # receive data and server address from server
#     data, server_address = client_socket.recvfrom(2048)
#
#     # check if the data is empty
#     if not data:
#         break
#
#     # write received data to file
#     f.write(data)
#
# # close the file and socket
# f.close()
# client_socket.close()

# import socket
# import time
#
# # create a TCP socket
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# # define the server address and port
# server_address = ('localhost', 5005)
#
# # connect to the server
# client_socket.connect(server_address)
#
# # send the available bandwidth to the server
# client_socket.send(str(2048).encode('utf-8'))
#
# # receive the video data from the server
# f = open('video.mp4', 'wb')
# while True:
#     data = client_socket.recv(2048)
#
#     if data == b'EOF':
#         break
#
#     f.write(data)
#
# f.close()
# client_socket.close()
#///////////////////
# import socket
#
# # create a TCP socket
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# print('y')
# # define the server address and port
# server_address = ('localhost', 5005)
# print('o')
# # connect to the server
# client_socket.connect(server_address)
#
# # send the available bandwidth to the server
# client_socket.send(str(2048).encode('utf-8'))
# print('v')
# # receive the video data from the server
# f = open('video.mp4', 'wb')
# print('e')
# while True:
#     data = client_socket.recv(2048)
#
#     if data == b'EOF':
#         break
#     print('l')
#     f.write(data)
#
# f.close()
# client_socket.close()
import socket

# create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# define the server address and port
server_address = ('localhost', 5005)

# connect to the server
client_socket.connect(server_address)

# send the available bandwidth to the server
client_socket.send(str(2048).encode('utf-8'))

# receive the video data from the server
f = open('video.mp4', 'wb')
bytes_received = 0
while True:
    data = client_socket.recv(2048)

    if not data:
        break

    bytes_received += len(data)

    f.write(data)
    print(f'{bytes_received} bytes received')
f.close()
client_socket.close()

print(f'{bytes_received} bytes received')




