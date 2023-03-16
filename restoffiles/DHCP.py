import threading
import socket

class DHCP:
    def __init__(self):
        self.address = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', 5555))
        self.ips = {}

    def listen(self):
        while True:
            message, self.address = self.sock.recvfrom(1024)
            print("DHCP: Received message from {}".format(self.address))
            thread = threading.Thread(target=self.handle_message, args=(message,))
            thread.start()

    def handle_message(self, message):
        # Parse the DHCP message
        op, htype, hlen, hops, xid, secs, flags, ciaddr, yiaddr, siaddr, giaddr, chaddr, options = self.parse_message(
            message)

        # Identify the message type
        message_type = None
        for option in options:
            if option[0] == 53:
                print("DHCP: Message type: {}".format(option[2][0]))
                message_type = int.from_bytes(option[2], byteorder='big')
                break

        # Generate the response based on the message type
        if message_type == 1:  # Discover
            print("DHCP: Sending Offer")
            response = self.generate_offer(xid, chaddr)
        elif message_type == 3:  # Request
            print("DHCP: Sending ACK")
            response = self.generate_ack(xid, yiaddr, chaddr)
        else:
            response = None

        # Send the response
        if response is not None:
            self.sock.sendto(response, self.address)

    def parse_message(self, message: bytes):
        """
        Parses a DHCP message and extracts the different fields.

        Args:
            message (bytes): the raw DHCP message bytes received over the network.

        Returns:
            A tuple containing the different fields of the DHCP message:
            - op (int): specifies whether the message is a request or a reply.
            - htype (int): specifies the type of hardware address being used (usually 1 for Ethernet).
            - hlen (int): specifies the length of the hardware address (usually 6 bytes for Ethernet).
            - hops (int): used by DHCP relay agents to forward DHCP messages across different subnets.
            - xid (bytes): a transaction ID used to match requests and replies.
            - secs (bytes): elapsed time since the client started trying to acquire or renew an IP address.
            - flags (bytes): contains flags that control the behavior of the DHCP client and server.
            - ciaddr (bytes): client IP address (optional).
            - yiaddr (bytes): your (client) IP address.
            - siaddr (bytes): server IP address (optional).
            - giaddr (bytes): gateway IP address (optional).
            - chaddr (bytes): client hardware address.
            - options (List[Tuple[int, int, bytes]]): a list of DHCP options, which contain additional configuration information for the client.
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

    def generate_offer(self, xid: bytes, chaddr: bytes) -> bytes:
        """
        Generates a DHCP Offer message in response to a DHCP Discover message.

        Args:
            xid (bytes): the transaction ID of the original DHCP Discover message.
            chaddr (bytes): the client hardware address from the original DHCP Discover message.

        Returns:
            A bytes object representing the raw DHCP Offer message.
        """
        # DHCP message fields
        op = 2  # Boot reply
        htype = 1  # Ethernet
        hlen = 6  # MAC address length
        hops = 0
        secs = 0
        flags = 0
        ciaddr = bytes([0] * 4)  # Client IP address
        yiaddr = bytes([192, 168, 0, 2])  # Your (client) IP address
        siaddr = bytes([0] * 4)  # Server IP address
        giaddr = bytes([0] * 4)  # Gateway IP address
        chaddr = chaddr  # Client hardware address

        # DHCP options
        message_type = bytes([53, 1, 2])  # DHCP message type: Offer
        subnet_mask = bytes([1, 4, 255, 255, 255, 0])  # Subnet mask
        router = bytes([3, 4, 192, 168, 0, 1])  # Router
        dns = bytes([6, 4, 8, 8, 8, 8, 0])  # DNS server
        lease_time = bytes([51, 4, 0, 0, 7, 68])  # IP address lease time: 1 day
        end_option = bytes([255])  # End option

        # Concatenate all DHCP options
        options = message_type + subnet_mask + router + dns + lease_time + end_option

        # Convert all fields to bytes
        op = op.to_bytes(1, byteorder='big')
        htype = htype.to_bytes(1, byteorder='big')
        hlen = hlen.to_bytes(1, byteorder='big')
        hops = hops.to_bytes(1, byteorder='big')
        secs = secs.to_bytes(2, byteorder='big')
        flags = flags.to_bytes(2, byteorder='big')

        # Concatenate DHCP message fields and options
        dhcp_message = op + htype + hlen + hops + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr + bytes(
            [0] * 10) + options

        return dhcp_message

    def generate_ack(self, xid: bytes, yiaddr: bytes, chaddr: bytes) -> bytes:
        """
        Generates a DHCP Ack message in response to a DHCP Request message.

        Args:
            xid (bytes): the transaction ID of the original DHCP Request message.
            yiaddr (bytes): the IP address offered to the client in the original DHCP Offer message.
            chaddr (bytes): the client hardware address from the original DHCP Request message.

        Returns:
            A bytes object representing the raw DHCP Ack message.
        """
        # DHCP message fields
        op = 2  # Boot reply
        htype = 1  # Ethernet
        hlen = 6  # MAC address length
        hops = 0
        secs = 0
        flags = 0
        ciaddr = bytes([0] * 4)  # Client IP address
        yiaddr = yiaddr  # Your (client) IP address
        siaddr = bytes([0] * 4)  # Server IP address
        giaddr = bytes([0] * 4)  # Gateway IP address
        chaddr = chaddr  # Client hardware address

        # DHCP options
        message_type = bytes([53, 1, 5])  # DHCP message type: Ack
        subnet_mask = bytes([1, 4, 255, 255, 255, 0])  # Subnet mask
        router = bytes([3, 4, 192, 168, 0, 1])  # Router
        dns = bytes([6, 4, 8, 8, 8, 8, 0])  # DNS server
        lease_time = bytes([51, 4, 0, 0, 7, 68])  # IP address lease time: 1 day
        end_option = bytes([255])  # End option

        # Concatenate all DHCP options
        options = message_type + subnet_mask + router + dns + lease_time + end_option

        # Convert all fields to bytes
        op = op.to_bytes(1, byteorder='big')
        htype = htype.to_bytes(1, byteorder='big')
        hlen = hlen.to_bytes(1, byteorder='big')
        hops = hops.to_bytes(1, byteorder='big')
        secs = secs.to_bytes(2, byteorder='big')
        flags = flags.to_bytes(2, byteorder='big')

        # Concatenate DHCP message fields and options
        dhcp_message = op + htype + hlen + hops + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr + bytes(
            [0] * 10) + options

        return dhcp_message

if __name__ == '__main__':
    dhcp = DHCP()
    dhcp.listen()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
