import sys
from scapy.all import *


openPort=[53,67]
for port in openPort:
	if port == 53:
		dns_reply=sr1(IP(dst="10.10.111.1")/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname="www.google.com")))
		dns_reply.show()
	if port== 67:
		conf.checkIPaddr=False
		fam,hw=get_if_raw_hwaddr(conf.iface)
		dhcp_discover=Ether(dst="ff:ff:ff:ff:ff:ff")/IP(src="0.0.0.0",dst="255.255.255.255")/UDP(sport=68,dport=67)/BOOTP(chaddr=hw)/DHCP(options=[("message-type","discover"),"end"])
		ans,unans=srp(dhcp_discover, multi=True)
		ans.summary()
		unans.summary()
		
