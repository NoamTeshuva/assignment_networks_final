# import socket
# import os
#
# # define the video directory
# VIDEO_DIR = '/Users/User/Videos'
#
#
# path_360 = os.path.join(VIDEO_DIR, "video_360p.mp4")
# path_480 = os.path.join(VIDEO_DIR, "video_480p.mp4")
# path_720 = os.path.join(VIDEO_DIR, "video_720p.mp4")
#
# bitrate_360 = 1024  # in kbps
# bitrate_480 = 2048  # in kbps
# bitrate_720 = 4096  # in kbps
#
# # calculate the bandwidth thresholds (in kbps)
# BANDWIDTH_THRESHOLDS = {
#     '360': bitrate_360,
#     '480': bitrate_480,
#     '720': bitrate_720
# }
#
# # create a TCP socket
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# server_address = ('localhost', 5005)
# server_socket.bind(server_address)
#
# print('Server started')
# server_socket.listen()  # listen for up to 5 clients
#
# while True:
#     client_socket, client_address = server_socket.accept()
#
#     print('New client connected:', client_address)
#
#     f_360 = open(path_360, 'rb')
#     f_480 = open(path_480, 'rb')
#     f_720 = open(path_720, 'rb')
#
#     try:
#         while True:
#             data = client_socket.recv(2048)
#
#             if not data:
#                 break
#
#             available_bandwidth = int(data.decode('utf-8'))
#
#             if available_bandwidth < BANDWIDTH_THRESHOLDS['360']:
#                 send_data = f_360.read(2048)
#
#             elif available_bandwidth < BANDWIDTH_THRESHOLDS['480']:
#                 send_data = f_480.read(int(bitrate_480 * 0.5))
#
#             elif available_bandwidth < BANDWIDTH_THRESHOLDS['720']:
#                 send_data = f_720.read(int(bitrate_720 * 0.5))
#
#             else:
#                 send_data = f_720.read(2048)
#
#             client_socket.sendall(send_data)
#
#         # send end-of-file message to client
#         client_socket.sendall(b'EOF')
#
#     except Exception as e:
#         print('Error:', e)
#
#     finally:
#         f_360.close()
#         f_480.close()
#         f_720.close()
#         client_socket.close()
#
# server_socket.close()
import socket
import os

# define the video directory
VIDEO_DIR = '/Users/User/Videos'

path_360 = os.path.join(VIDEO_DIR, "video_360p.mp4")
path_480 = os.path.join(VIDEO_DIR, "video_480p.mp4")
path_720 = os.path.join(VIDEO_DIR, "video_720p.mp4")

bitrate_360 = 1024  # in kbps
bitrate_480 = 2048  # in kbps
bitrate_720 = 4096  # in kbps

# calculate the bandwidth thresholds (in kbps)
BANDWIDTH_THRESHOLDS = {
    '360': bitrate_360,
    '480': bitrate_480,
    '720': bitrate_720
}

# create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 5005)
server_socket.bind(server_address)

print('Server started')
server_socket.listen()  # listen for up to 5 clients

while True:
    client_socket, client_address = server_socket.accept()

    print('New client connected:', client_address)

    f_360 = open(path_360, 'rb')
    f_480 = open(path_480, 'rb')
    f_720 = open(path_720, 'rb')

    try:
        while True:
            print('y')
            data = client_socket.recv(2048)

            if not data:
                print('o')
                break

            available_bandwidth = int(data.decode('utf-8'))

            if available_bandwidth < BANDWIDTH_THRESHOLDS['360']:
                print('v')
                send_data = f_360.read(2048)

            elif available_bandwidth < BANDWIDTH_THRESHOLDS['480']:
                print('e')
                send_data = f_480.read(int(bitrate_480 * 0.5))

            elif available_bandwidth < BANDWIDTH_THRESHOLDS['720']:
                print('l')
                send_data = f_720.read(int(bitrate_720 * 0.5))

            else:
                print('z')
                send_data = f_720.read(2048)

            client_socket.sendall(send_data)

        # send end-of-file message to client
        client_socket.sendall(b'EOF')

    except Exception as e:
        print('Error:', e)

    finally:
        f_360.close()
        f_480.close()
        f_720.close()
        client_socket.close()

server_socket.close()

