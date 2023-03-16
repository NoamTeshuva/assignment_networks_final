import socket
import struct
import random
import time
import os

N_CHUNKS = 2
MSS = 63000


class TCPOverUDPSender:
    """
    A class that implements a TCP-over-UDP sender.

    ...

    Attributes
    ----------
    available_space : int
        The available space in the sender's buffer.
    server_address : str
        The IP address of the server that the sender will communicate with.
    server_port : int
        The port number of the server that the sender will communicate with.
    window_size : int
        The size of the sender's window.
    timeout : float
        The timeout for the sender's socket.
    seq_num : int
        The sequence number for the sender's packets.
    unacked_packets : list
        The list of packets that have been sent but not yet acknowledged.
    socket : socket
        The sender's socket for communicating with the server.
    congestion_control : bool
        A flag indicating whether congestion control is enabled.
    slow_start_threshold : int
        The slow start threshold for congestion control.
    cwnd : int
        The congestion window for congestion control.
    num_acks : int
        The number of acknowledgments received by the sender.
    client_address : tuple
        The IP address and port number of the client that the sender is communicating with.

    Methods
    -------
    run(data):
        Implements the initial 3-way handshake protocol to establish a reliable connection between a TCP-over-UDP server and a client. Once the connection is established, it sends the data to the client.
    create_packet(syn=False, ack=False, fin=False, seq_num=None, ack_num=None, data=None):
        Creates a packet with the given flags, sequence number, acknowledgment number, and data.
    parse_packet(packet):
        Parses a packet into its components.
    send(data):
        Sends the data to the client using TCP-over-UDP.
"""

    def __init__(self, server_address='127.0.0.1', server_port=55555, window_size=10, timeout=0.5,
                 congestion_control=True):
        """
        Initializes the TCPOverUDPSender object with default values for server_address, server_port, window_size, timeout, and congestion_control.
        
        Parameters
        ----------
        server_address : str, optional
            The IP address of the server that the sender will communicate with. Default is '127.0.0.1'.
        server_port : int, optional
            The port number of the server that the sender will communicate with. Default is 55555.
        window_size : int, optional
            The size of the sender's window. Default is 10.
        timeout : float, optional
            The timeout for the sender's socket. Default is 0.5.
        congestion_control : bool, optional
            A flag indicating whether congestion control is enabled. Default is True.
        """
        self.available_space = MSS * window_size
        self.server_address = server_address
        self.server_port = server_port
        self.window_size = window_size
        self.timeout = timeout
        self.seq_num = random.randint(0, 2 ** 32 - 1)
        self.unacked_packets = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('localhost', server_port))
        self.congestion_control = congestion_control
        self.slow_start_threshold = window_size * MSS // 2
        self.cwnd = MSS
        self.num_acks = 0
        self.client_address = None

    def run(self, data):
        """
        Runs the TCP server, receiving and sending packets as necessary to transfer the given data.
        :param data: the data to transfer
        """
        while True:
            # Wait for SYN packet
            print('Waiting for SYN packet')
            syn_packet, self.client_address = self.socket.recvfrom(MSS)
            self.socket.settimeout(self.timeout)
            syn_packet_dict = self.parse_packet(syn_packet)

            if syn_packet_dict.get('syn'):
                print('Received SYN packet')
                self.seq_num = random.randint(0, 2 ** 32 - 1)
                break

        # Send SYN-ACK packet
        print('Sending SYN-ACK packet')
        syn_ack_packet = self.create_packet(syn=True, ack=True, ack_num=syn_packet_dict['seq_num'] + 1)
        self.socket.sendto(syn_ack_packet, self.client_address)

        # Receive ACK packet
        print('Waiting for ACK packet')
        ack_packet, address = self.socket.recvfrom(MSS)

        if address != self.client_address:
            print('Received ACK packet from wrong address')
            return

        ack_packet_dict = self.parse_packet(ack_packet)

        if ack_packet_dict.get('ack'):
            print('Received ACK packet')
            self.seq_num = ack_packet_dict['ack_num']

        # Send data
        self.send(data)

    def create_packet(self, syn=False, ack=False, fin=False, seq_num=None, ack_num=None, data=None):
        """
        Creates a TCP packet with the given flags, sequence number, acknowledgement number, and data.
        :param syn: whether or not this is a SYN packet
        :param ack: whether or not this is an ACK packet
        :param fin: whether or not this is a FIN packet
        :param seq_num: the sequence number to use for the packet, or None to use the server's current sequence number
        :param ack_num: the acknowledgement number to use for the packet, or None to use zero
        :param data: the data to include in the packet, or None for no data
        :return: the binary representation of the packet
        """

        # Calculate flags based on input values
        flags = (syn << 2) | (ack << 1) | fin

        # Pack the packet fields into binary format
        packet = struct.pack('!IIHH', seq_num or self.seq_num, ack_num or 0, flags, self.window_size)

        # Append data to the packet if provided
        if data:
            packet += data

        # Print the size of the packet and return the packet
        print('Size of packet: {}'.format(len(packet)))
        return packet

    def parse_packet(self, packet):
        """
        Parses a binary TCP packet and returns its fields as a dictionary.
        :param packet: the binary representation of the packet
        :return: a dictionary containing the parsed packet fields
        """

        # Unpack the packet into its components
        seq_num, ack_num, flags, window_size = struct.unpack('!IIHH', packet[:12])

        # Extract the SYN, ACK, and FIN flags from the flags byte
        syn = flags & 4 == 4
        ack = flags & 2 == 2
        fin = flags & 1 == 1

        # Extract the packet data (if any)
        data = packet[12:]

        # Return a dictionary containing the parsed packet components
        return {
            'seq_num': seq_num,
            'ack_num': ack_num,
            'syn': syn,
            'ack': ack,
            'fin': fin,
            'data': data
        }

    def send(self, data):
        """
        Sends the given data to the client using the TCP protocol.
        :param data: the data to send
        """

        # Break data into chunks of size MSS bytes or less
        # chunks = [data[i:i + MSS] for i in range(0, len(data), MSS)]

        chunk_length = int(len(data) / N_CHUNKS)
        chunks = []
        for i in range(0, N_CHUNKS):
            if i == N_CHUNKS - 1:
                chunks += [data[i * chunk_length:]]
            else:
                chunks += [data[i * chunk_length: i * chunk_length]]
        print('Sending {} chunks'.format(len(chunks)))
        sent_packets = []

        # Keep sending packets until all chunks have been sent and all packets have been acknowledged
        while chunks or self.unacked_packets:

            # Send new packets
            while len(self.unacked_packets) < min(self.window_size,
                                                  self.cwnd // MSS) and chunks and self.available_space > 0:
                # Take the next chunk to send
                chunk = chunks.pop(0)
                self.seq_num += len(chunk)
                # Create a packet with the chunk of data
                packet = self.create_packet(data=chunk)
                print('Sending packet with seq_num {}'.format(self.seq_num))
                # Send the packet to the client
                self.socket.sendto(packet, self.client_address)
                # Keep track of the sent packet and the time it was sent
                sent_packets.append((self.seq_num, time.time()))
                # Update the sequence number and the list of unacknowledged packets
                print(f"chunk length: {len(chunk)}")
                self.unacked_packets.append(packet)
                # Update the available space in the buffer
                self.available_space -= len(chunk)
                # Congestion control
                if self.congestion_control:
                    self.cwnd += MSS
                    if self.cwnd > self.slow_start_threshold:
                        self.cwnd += MSS / self.cwnd
                    else:
                        break

            # Receive ACKs
            try:
                # Wait for an ACK packet from the client
                ack_packet, address = self.socket.recvfrom(MSS)

                # Check if the packet came from the expected address
                if address != self.client_address:
                    print('Received ACK packet from wrong address')
                    return

                # Parse the ACK packet to extract its fields
                ack_packet_dict = self.parse_packet(ack_packet)
                if ack_packet_dict.get('ack'):
                    ack_num = ack_packet_dict['ack_num']
                    print('Received ACK packet with ack_num {}'.format(ack_num))
                    # Look for the sent packet that matches the ACK number
                    for i in range(len(self.unacked_packets)):
                        if i >= len(self.unacked_packets):
                            break

                        packet = self.unacked_packets[i]
                        if struct.unpack('!I', packet[:4])[0] == ack_num - MSS:
                            # Remove the acknowledged packet from the list of unacknowledged packets
                            self.unacked_packets.pop(i)
                            # Update congestion control parameters
                            self.num_acks += 1
                            if self.congestion_control:
                                if self.num_acks == self.window_size:
                                    self.num_acks = 0
                                    self.window_size += 1
                                    self.cwnd += MSS / self.cwnd
                                else:
                                    self.cwnd += MSS / self.cwnd
                            # Update the available space in the buffer
                            self.available_space += len(packet) - 12
                            break
            except:
                # If no ACK is received, wait for the next timeout interval
                pass

            # Check for timed-out packets
            i = 0
            print('length of sent packets: {}'.format(len(sent_packets)))
            while i < len(sent_packets):
                print('Checking for timed-out packets')
                seq_num, send_time = sent_packets[i]
                print('Packet with seq_num {} sent at {}'.format(seq_num, send_time))

                if time.time() - send_time > self.timeout:
                    # If the packet has timed out
                    if i >= len(self.unacked_packets):
                        # If there are no more packets in unacked_packets
                        break

                    # Get the packet from unacked_packets
                    packet = self.unacked_packets[i]
                    print('Packet with seq_num {} timed out'.format(seq_num))

                    # Resend the packet
                    self.socket.sendto(packet, self.client_address)
                    sent_packets[i] = (seq_num, time.time())

                    # If congestion control is enabled, perform congestion control
                    if self.congestion_control:
                        self.slow_start_threshold = max(self.window_size // 2, 1)
                        self.window_size = 1
                        self.cwnd = self.window_size * MSS
                        self.available_space += len(packet) - 12
                        i += 1
                else:
                    i += 1

        print('Finished sending data')
        # All data has been sent, close the connection
        self.close()

    def close(self):
        """
        Closes the connection by sending a FIN packet and waiting for a FIN-ACK packet.
        If all packets have been acknowledged, sends an ACK packet to confirm the connection is closed.
        """

        # Send FIN packet when all packets have been sent
        print(self.unacked_packets)
        if not self.unacked_packets:
            fin_packet = self.create_packet(fin=True)
            print('Sending FIN packet')
            self.socket.sendto(fin_packet, self.client_address)

            # Wait for FIN-ACK packet
            while True:
                fin_ack_packet, address = self.socket.recvfrom(MSS)

                if address != self.client_address:
                    print('Received FIN-ACK packet from wrong address')
                    continue

                print('Received FIN-ACK packet')
                fin_ack_packet_dict = self.parse_packet(fin_ack_packet)

                if fin_ack_packet_dict.get('fin') and fin_ack_packet_dict.get('ack'):
                    ack_packet = self.create_packet(ack=True, ack_num=fin_ack_packet_dict['seq_num'] + 1)
                    print('Sending ACK packet')
                    self.socket.sendto(ack_packet, self.client_address)
                    break

        # Close the socket
        self.socket.close()


if __name__ == '__main__':
    data = os.urandom(MSS * 1)
    # data = # Open the image file
    # with open('1.png', 'rb') as f:
    #     data = f.read()

    sender = TCPOverUDPSender()
    sender.run(data)
