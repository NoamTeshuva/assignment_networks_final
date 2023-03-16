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
while True:
    data = client_socket.recv(2048)

    if not data:
        break

    if data == b'EOF':
        break

    f.write(data)

f.close()
client_socket.close()
print("Video transfer completed.")
