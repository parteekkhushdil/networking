import sys
from scapy.all import *

closedPort=[]
openPort=[]

for port in range(1,101):
	source_port=RandShort()
	ans=sr1(IP(dst="10.10.111.1")/UDP(sport=source_port,dport=port),retry=-2,timeout=5)
	if (str(type(ans))=="<type 'NoneType'>"):
		openPort.append(port)
				
	elif(ans.haslayer(UDP)):
		openPort.append(port)
	elif(ans.haslayer(ICMP)):
		closedPort.append(port)
				
print "Open Ports " ,openPort
print "Closed Ports " , closedPort

