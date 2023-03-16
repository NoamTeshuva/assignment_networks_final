import socket

class DNS:
    def __init__(self, server_address='127.0.0.1', port=30552):
        """
        Constructor, initializes the cache.
        """
        self.cache = {
            'myapp.com': {
                'ip': server_address,
                'port': port
            }
        }

    def get_ip_address(self, domain_name):
        """
        Get the IP address by a given name
        :param domain_name: the domain name
        :return: the IP address
        """
        return self.cache.get(domain_name, {}).get('ip')

    def get_port(self, domain_name):
        """
        Get the port number by a given name
        :param domain_name: the domain name
        :return: the port number
        """
        return self.cache.get(domain_name, {}).get('port')

    def add_record(self, domain_name, ip_address, port):
        """
        Add a new record to the cache
        :param domain_name: the domain name
        :param ip_address: the IP address
        :param port: the port number
        :return:
        """
        self.cache[domain_name] = {
            'ip': ip_address,
            'port': port
        }

    def remove_record(self, domain_name):
        """
        Remove a record from the cache
        :param domain_name: the domain name
        :return: NA
        """
        self.cache.pop(domain_name, None)

    def handle_dns_packet(self, packet):
        """
        Handle a DNS packet
        :param packet: THE packet
        :return: the IP address and port number
        """
        parts = packet.split(':')
        if len(parts) != 2 or parts[0] != 'GET_IP':
            return None, None
        domain_name = parts[1]
        ip_address = self.get_ip_address(domain_name)
        port = self.get_port(domain_name)
        if not ip_address or not port:
            return None, None
        return ip_address, port

    def listen(self, port=5552):
        """
        Listen for DNS requests
        :param port: the port number
        :return: NA
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', port))
        print(f'Listening on port {port}')
        while True:
            data, addr = sock.recvfrom(1024)
            print(f'Received {data} from {addr}')
            ip_address, port = self.handle_dns_packet(data.decode())
            if ip_address and port:
                response = f'{ip_address}:{port}'
            else:
                response = 'None:None'
            sock.sendto(response.encode(), addr)

    def run(self):
        """
        Runs the DNS server indefinitely.
        """
        self.listen()

if __name__ == '__main__':
    dns = DNS()
    dns.run()