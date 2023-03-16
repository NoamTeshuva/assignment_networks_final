import socket
import os

# define the video directory
VIDEO_DIR = '/video/'

path_360 = os.path.join(VIDEO_DIR, "video_360p.mp4")
path_480 = os.path.join(VIDEO_DIR, "video_480p.mp4")
path_720 = os.path.join(VIDEO_DIR, "video_720p.mp4")

size_360 = os.path.getsize(path_360)
size_480 = os.path.getsize(path_480)
size_720 = os.path.getsize(path_720)

bandWidth_720 = size_720 / 2048
bandWidth_480 = size_480 / bandWidth_720
bandWidth_360 = size_360 / bandWidth_720

f_360 = open(path_360, 'rb')
f_480 = open(path_480, 'rb')
f_720 = open(path_720, 'rb')

# define the available bandwidth thresholds (in kbps)
BANDWIDTH_THRESHOLDS = {
    '360': bandWidth_360,
    '480': bandWidth_480,
    '720': bandWidth_720
}

# create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 5005)
server_socket.bind(server_address)

print('Server started')
while True:
    while True:
        data_720 = f_720.read(2048)
        data_480 = f_480.read(int(bandWidth_480))
        data_360 = f_360.read(int(bandWidth_360))

        data_, client_address = server_socket.recvfrom(2048)

        available_bandwidth = int(data_.decode('utf-8'))
        
        if available_bandwidth < BANDWIDTH_THRESHOLDS['360']:
            send_data = data_360

        elif available_bandwidth < BANDWIDTH_THRESHOLDS['480']:
            send_data = data_480

        elif available_bandwidth < BANDWIDTH_THRESHOLDS['720']:
            send_data = data_720

        else:
            send_data = data_720

        server_socket.sendto(send_data, client_address)

        if not send_data:
            break

# close the socket
server_socket.close()