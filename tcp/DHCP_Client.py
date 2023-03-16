import random
import socket
PORT = 20510

class DHCP_Client:
    def __init__(self, interface_name):
        """
        Initialize the DHCP client.

        Args:
        - interface_name (str): the name of the interface to use for DHCP communication.
        """
        self.interface_name = interface_name
        self.ip_address = None
        self.mac_address = self.generate_mac_address()
        self.transaction_id = random.randint(1, 2**32 - 1)
        self.server_ip = 'localhost'
        self.server_port = PORT

        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', 5554))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def generate_mac_address(self):
        """
        Generate a random MAC address in the format xx:xx:xx:xx:xx:xx.

        Args:
        - None

        Returns:
        - str: the generated MAC address.
        """
        mac_address = [0x00, 0x16, 0x3e,
                       random.randint(0x00, 0x7f),
                       random.randint(0x00, 0xff),
                       random.randint(0x00, 0xff)]
                       
        return ':'.join(map(lambda x: "%02x" % x, mac_address))

    def generate_discover(self):
        """
        Generate a DHCP Discover message.

        Args:
        - None

        Returns:
        - bytes: the raw DHCP Discover message.
        """
        # DHCP message fields
        op = 1  # Boot request
        htype = 1  # Ethernet
        hlen = 6  # MAC address length
        hops = 0
        xid = self.transaction_id.to_bytes(4, byteorder='big')
        secs = bytes([0, 0])
        flags = bytes([0, 0])
        ciaddr = bytes([0] * 4)  # Client IP address
        yiaddr = bytes([0] * 4)  # Your (client) IP address
        siaddr = bytes([0] * 4)  # Server IP address
        giaddr = bytes([0] * 4)  # Gateway IP address
        chaddr = bytes.fromhex(self.mac_address.replace(':', ''))  # Client hardware address

        # DHCP options
        message_type = bytes([53, 1, 1])  # DHCP message type: Discover
        parameter_request_list = bytes([55, 6, 1, 3, 6, 15, 28, 51])  # Parameter request list
        client_identifier = bytes([61, 7]) + chaddr  # Client identifier
        end_option = bytes([255])  # End option

        # Concatenate all DHCP options
        options = message_type + parameter_request_list + client_identifier + end_option

        # Concatenate DHCP message fields and options
        dhcp_message = bytes(
            [op, htype, hlen, hops]) + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr + bytes(
            [0] * 10) + options

        return dhcp_message

    def send_discover(self):
        """
        Send a DHCP Discover message.

        Args:
        - None

        Returns:
        - None
        """
        # Generate DHCP Discover message
        discover_message = self.generate_discover()

        # Send DHCP Discover message
        self.sock.sendto(discover_message, ('localhost', 5555))

        print('DHCP Discover message sent.')

    def generate_request(self, xid, chaddr, lease_time, server_ip='127.0.0.1', yiaddr=bytes([0] * 4), requested_ip=None):
        """
        Generates a DHCP Request message in response to a DHCP Offer message.
        Args:
        - xid (bytes): Transaction ID.
        - chaddr (bytes): Client hardware address.
        - lease_time (int): The time in seconds for which the lease should be granted.
        - server_ip (str): The IP address of the DHCP server.
        - yiaddr (bytes): The client's (your) IP address.
        - requested_ip (str): The requested IP address (optional).

        Returns:
        - bytes: A bytes object representing the raw DHCP Request message.
        """

        # DHCP message fields
        op = 1  # Boot request
        htype = 1  # Ethernet
        hlen = 6  # MAC address length
        hops = 0
        xid = xid  # Transaction ID
        secs = bytes([0, 0])  # Elapsed time since client started trying to acquire or renew IP address
        flags = bytes([0, 0])  # Flags (unused)
        ciaddr = bytes([0] * 4)  # Client IP address
        yiaddr = yiaddr  # Your (client) IP address
        siaddr = socket.inet_aton(server_ip)  # Server IP address
        giaddr = bytes([0] * 4)  # Gateway IP address
        chaddr = chaddr  # Client hardware address

        # DHCP options
        message_type = bytes([53, 1, 3])  # DHCP message type: Request
        server_id = bytes([54, 4]) + siaddr  # DHCP server identifier
        requested_ip_option = bytes([50, 4]) + socket.inet_aton(requested_ip) if requested_ip else b''
        lease_time_option = bytes([51, 4]) + lease_time.to_bytes(4, byteorder='big')
        end_option = bytes([255])  # End option

        # Concatenate all DHCP options
        options = message_type + server_id + requested_ip_option + lease_time_option + end_option

        # Convert all fields to bytes
        op = op.to_bytes(1, byteorder='big')
        htype = htype.to_bytes(1, byteorder='big')
        hlen = hlen.to_bytes(1, byteorder='big')
        hops = hops.to_bytes(1, byteorder='big')
        secs = secs
        flags = flags

        # Concatenate DHCP message fields and options
        dhcp_message = op + htype + hlen + hops + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr + bytes(
            [0] * 10) + options

        # Returns A bytes object representing the raw DHCP Request message.
        return dhcp_message

    def parse_message(self, message: bytes):
        """
        Parses a DHCP message and extracts the different fields.

        Args:
        - message (bytes): A bytes object representing the raw DHCP message.

        Returns:
        - tuple: A tuple containing the different fields extracted from the DHCP message.
        """
        
        op = message[0]
        htype = message[1]
        hlen = message[2]
        hops = message[3]
        xid = message[4:8]
        secs = message[8:10]
        flags = message[10:12]
        ciaddr = message[12:16]
        yiaddr = message[16:20]
        siaddr = message[20:24]
        giaddr = message[24:28]
        chaddr = message[28:34]
        options = []

        # Parse DHCP options
        while len(options) < len(message) - 34:
            option = message[34 + len(options):]
            if option[0] == 255:
                # End of options
                break
            option_code = option[0]
            option_len = option[1]
            option_data = option[2:2 + option_len]
            options.append((option_code, option_len, option_data))


        return op, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr, options

    def generate_transaction_id(self):
        """
        Generates a random transaction ID for use in DHCP messages.

        :return: A bytes object containing the transaction ID.
        """
        transaction_id = bytearray(4)

        for i in range(4):
            transaction_id[i] = random.randint(0, 255)
        
        # Returns A bytes object containing the transaction ID.
        return bytes(transaction_id)

    def receive_offer(self):
        """
        Receives a DHCP Offer message from the DHCP server.

        :return: A bytes object containing the offered IP address, or None if no offer was received.
        """
        while True:
            message, address = self.sock.recvfrom(1024)
            print('Received DHCP Offer message from server.')

            # Parse DHCP Offer message
            op, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr, options = self.parse_message(
                message)

            print('IP address offered: {}'.format(socket.inet_ntoa(yiaddr)))

            print('Transaction ID: {}'.format(xid.hex()))

            # Check if message is a DHCP Offer
            message_type = None
            for option in options:
                if option[0] == 53:
                    print('Message type: Offer', message_type)
                    message_type = 2
                    break

            if message_type == 2:
                return yiaddr

    def send_request(self, offered_ip):
        """
        Sends a DHCP Request message to the DHCP server.

        :param offered_ip: A bytes object containing the offered IP address to request.
        :return: A bytes object containing the assigned IP address, or None if no address was assigned.
        """

        # Generate DHCP Request message
        transaction_id = self.generate_transaction_id()
        chaddr = bytes.fromhex(self.mac_address.replace(':', ''))  # Client hardware address
        dhcp_request = self.generate_request(transaction_id, chaddr, yiaddr=offered_ip, lease_time=86400)

        # Send DHCP Request message
        print('Sending DHCP Request message to server.')
        self.sock.sendto(dhcp_request, ('localhost', 5555))

        # Receive DHCP Ack message
        self.sock.settimeout(10)  # Wait up to 10 seconds for a response
        try:
            yiaddr = self.receive_ack()
        except socket.timeout:
            print('No DHCP Ack message received from server.')
            return None
        else:
            return yiaddr

    def receive_ack(self):
        """
        Receives a DHCP Ack message from the DHCP server.

        :return: A bytes object containing the assigned IP address, or None if no address was assigned.
        """
        while True:
            message, address = self.sock.recvfrom(1024)
            print('Received DHCP Ack message from server.')

            # Parse DHCP Ack message
            op, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr, options = self.parse_message(
                message)

            # Check if message is a DHCP Ack
            message_type = None
            for option in options:
                if option[0] == 53:
                    print('Message type: Ack')
                    message_type = 5
                    break

            if message_type == 5:
                return yiaddr

    def run(self):
        """
        Runs the DHCP client.

        Generates and sends a DHCP Discover message, receives and processes a DHCP Offer message,
        generates and sends a DHCP Request message, receives and processes a DHCP Ack message,
        and prints the assigned IP address.
        """
        
        self.send_discover()

        # Receive DHCP Offer message
        offered_ip = self.receive_offer()

        # Generate and send DHCP Request message
        assigned_ip = self.send_request(offered_ip)

        # Print assigned IP address
        if assigned_ip:
            print('Assigned IP address:', '.'.join(map(str, assigned_ip)))
            return '.'.join(map(str, assigned_ip))
        else:
            print('Failed to obtain IP address.')


if __name__ == '__main__':
    client = DHCP_Client(1)
    client.run()