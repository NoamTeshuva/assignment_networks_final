import socket
import struct
import random


class TCPOverUDPReceiver:
    def __init__(self, address='127.0.0.1', port=55552, server_port=55555, window_size=10, MSS=60000):
        """
            Constructor: initialize the cache.
            :param address: the IP address of the receiver.
            :param port: the port of the receiver
            :param server_port: the port of the server.
            :param window_size: window size of the receiver.
            :param MSS: MSS
            """
        self.BUFFER_SIZE = 65536
        self.MSS = MSS
        self.address = address
        self.port = port
        self.window_size = window_size
        self.expected_seq_num = 0
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.address, self.port))
        self.buffer = {}
        self.seq_num = random.randint(0, 2 ** 32 - 1)

    def run(self):
        """
        run and receive new packages.
        :return:
        """
        # Send SYN packet
        print('Sending SYN packet')
        syn_packet = self.create_packet(syn=True, seq_num=self.seq_num)
        self.socket.sendto(syn_packet, (self.address, self.server_port))

        # Wait for SYN-ACK packet
        while True:
            print('Waiting for SYN-ACK packet')
            syn_ack_packet, address = self.socket.recvfrom(self.BUFFER_SIZE)
            syn_ack_packet_dict = self.parse_packet(syn_ack_packet)
            print(syn_ack_packet_dict)
            if syn_ack_packet_dict.get('syn') and syn_ack_packet_dict.get('ack'):
                print('Received SYN-ACK packet')
                self.expected_seq_num = syn_ack_packet_dict['seq_num'] + 1
                break

        # Send ACK packet
        ack_packet = self.create_packet(ack=True, ack_num=self.expected_seq_num)
        self.socket.sendto(ack_packet, address)

        # Receive data packets
        while True:
            packet, address = self.socket.recvfrom(self.BUFFER_SIZE)
            packet_dict = self.parse_packet(packet)
            if packet_dict.get('seq_num') == self.expected_seq_num:
                print('Received packet with seq_num = {}'.format(self.expected_seq_num))
                data = packet_dict['data']
                self.buffer[self.expected_seq_num] = data
                self.expected_seq_num += 1  # Change this line

                # Send cumulative ACK packet
                while self.expected_seq_num in self.buffer:
                    print('Sending ACK packet with ack_num = {}'.format(self.expected_seq_num))
                    data = self.buffer.pop(self.expected_seq_num)
                    self.expected_seq_num += 1  # Change this line
                ack_packet = self.create_packet(ack=True, ack_num=self.expected_seq_num)
                self.socket.sendto(ack_packet, address)

            # Send ACK packet for out-of-order packet
            elif packet_dict.get('seq_num') != self.expected_seq_num:
                print('Sending ACK packet with ack_num = {}'.format(self.expected_seq_num))
                ack_packet = self.create_packet(ack=True, ack_num=self.expected_seq_num)
                self.socket.sendto(ack_packet, address)

            if packet_dict.get('fin'):
                fin_ack_packet = self.create_packet(fin=True, ack=True, ack_num=self.expected_seq_num)
                # Print data
                self.socket.sendto(fin_ack_packet, address)
                break

    def create_packet(self, syn=False, ack=False, fin=False, seq_num=None, ack_num=None, data=None):
        """

            :param syn: SYN flag
            :param ack: ack flag
            :param fin: fin flag
            :param seq_num: sqeunce number
            :param ack_num: ack number
            :param data: the data to be sent
            :return: the packet
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
        # Unpack the packet into its components
        seq_num, ack_num, flags, window_size = struct.unpack('!IIHH', packet[:12])

        # Extract the SYN, ACK, and FIN flags from the flags byte
        syn = flags & 4 == 4
        ack = flags & 2 == 2
        fin = flags & 1 == 1
        data = packet[12:]

        return {
            'seq_num': seq_num,
            'ack_num': ack_num,
            'syn': syn,
            'ack': ack,
            'fin': fin,
            'data': data

        }


if __name__ == '__main__':
    receiver = TCPOverUDPReceiver()
    receiver.run()
