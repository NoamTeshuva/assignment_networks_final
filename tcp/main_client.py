import time

from DHCP_Client import DHCP_Client
from DNS_Client import DNS_Client
from tcp_reciever import tcp_reciever


print("starting dhcp session")
a = DHCP_Client(1)
print(f"returned value: {a.run()}")
print("finished dhcp session starting dns session")
b = DNS_Client()
answer = b.run()
print(f"returned value: {answer}")
print("finished dns session starting app session")
c = tcp_reciever(answer)
c.run()
