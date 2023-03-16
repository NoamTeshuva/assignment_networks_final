import socket

class DNS_Client:
    """
    A DNS client that sends a DNS request packet to a DNS server to retrieve the IP address and port number
    of a specified domain name.
    
    """

    def __init__(self, server_address=('localhost', 5552)):
        """
        Initializes the DNS_Client object with the address of the DNS server and creates a socket object
        for sending and receiving packets.

        Args:
            server_address (tuple, optional): The address of the DNS server in the format of a tuple (hostname, port).
                Defaults to ('localhost', 5552).
        """
        self.server_address = server_address
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def get_ip_address(self, domain_name):
        """
        Sends a DNS request packet to the DNS server for a given domain name. Retrieves the IP address and port number
        from the response packet.

        Args:
            domain_name (str): The domain name for which to retrieve the IP address and port number.

        Returns:
            tuple: A tuple containing the IP address and port number of the specified domain name.
        """
        packet = f'GET_IP:{domain_name}'
        self.s.sendto(packet.encode(), self.server_address)
        data, _ = self.s.recvfrom(1024)
        response = data.decode().split(':')

        if len(response) == 2:
            ip_address, port = response

            if ip_address != 'None' and port != 'None':
                return ip_address, int(port)

        return None, None

    def run(self, domain_name='myapp.com'):
        """
        Runs the DNS client and retrieves the IP address and port number for the specified domain name
        from the DNS server.

        Args:
            domain_name (str, optional): The domain name for which to retrieve the IP address and port number.
                Defaults to 'myapp.com'.
        """
        ip_address, port = self.get_ip_address(domain_name)

        if ip_address:
            print(f'{domain_name} has IP address {ip_address} and port: {port}')
        else:
            print(f'{domain_name} not found')

if __name__ == '__main__':
    client = DNS_Client()
    client.run()
