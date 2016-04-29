import sys
from scapy.all import *

closedPort=[]
openPort=[]
filteredPort=[]
for port in range(0,100):
	source_port=RandShort()
	syn_ack=sr1(IP(dst="10.10.111.1")/TCP(sport=source_port,dport=port,flags="S"),retry=2,timeout=2)
	if (str(type(syn_ack))=="<type 'NoneType'>"):
		filteredPort.append(port)		
	elif syn_ack.haslayer(TCP):
		if syn_ack.getlayer(TCP).flags==0x12:
			openPort.append(port)
		elif syn_ack.getlayer(TCP).flags==0x14:
			closedPort.append(port)
		rst=send(IP(dst="10.10.111.1")/TCP(sport=source_port,dport=port,flags="R"))
print "Open Ports " ,openPort
print "Closed Ports " , closedPort
print "Filtered Ports ", filteredPort
