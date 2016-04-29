from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER,CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet,arp
from ryu.lib.packet import ether_types
class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
    	
    def __init__(self, *args, **kwargs):
      	super(SimpleSwitch, self).__init__(*args, **kwargs)
	self.s1={}
	self.s2={}
    def add_flow(self, datapath, in_port, dst,ipv4_src,ipv4_dst, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(in_port=in_port, dl_dst=haddr_to_bin(dst))
        mod = datapath.ofproto_parser.OFPFlowMod(datapath=datapath, match=match, cookie=0,
        command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
        priority=ofproto.OFP_DEFAULT_PRIORITY,
        flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        datapath.send_msg(mod)
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def _switch_features_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
	dpid=datapath.id
	if dpid==1:
	   self.s1=datapath
	else:
	    self.s2=datapath	
		

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        port = msg.in_port
        pkt = packet.Packet(data=msg.data)
        self.logger.info("packet-in %s" % (pkt,))
        pkt_ethernet = pkt.get_protocol(ethernet.ethernet)
        if not pkt_ethernet:
           return
        pkt_arp = pkt.get_protocol(arp.arp)
        if pkt_arp:
           self._handle_arp(datapath, port, pkt_ethernet, pkt_arp)
           return
    def _handle_arp(self, datapath, port, pkt_ethernet, pkt_arp):
        if pkt_arp.opcode != arp.ARP_REQUEST:
           return
	parser = datapath.ofproto_parser
        if pkt_arp.src_ip=='10.0.0.1' and pkt_arp.dst_ip=='10.0.0.2' and port == 1:	
		pkt = packet.Packet()
                pkt.add_protocol(ethernet.ethernet(ethertype=pkt_ethernet.ethertype,dst=pkt_ethernet.src,src='00:00:00:00:00:02'))
                pkt.add_protocol(arp.arp(opcode=arp.ARP_REPLY,src_mac='00:00:00:00:00:02',src_ip='10.0.0.2',dst_mac=pkt_arp.src_mac,
                               dst_ip=pkt_arp.src_ip))
                action1 = [parser.OFPActionOutput(port=2)]
	        action2=  [parser.OFPActionOutput(port=1)]
	        self.add_flow((self.s1), 1 , '00:00:00:00:00:02','10.0.0.1','10.0.0.2', action1)
		self.logger.info("Input port 1, ether type %s, source ip 10.0.0.1, destination ip 10.0.0.2",pkt_ethernet.ethertype) 
	        self.add_flow((self.s1), 2,'00:00:00:00:00:01','10.0.0.2','10.0.0.1', action2)
		self.logger.info("Input port 2, ether type %s, source ip 10.0.0.2, destination ip 10.0.0.1",pkt_ethernet.ethertype)
	        self.add_flow((self.s2), 1,'00:00:00:00:00:01','10.0.0.2','10.0.0.1', action1)
		self.logger.info("Input port 1, ether type %s, source ip 10.0.0.2, destination ip 10.0.0.1",pkt_ethernet.ethertype )
	        self.add_flow((self.s2), 2,'00:00:00:00:00:02','10.0.0.1','10.0.0.2', action2)		
	        self.logger.info("Input port 2, ether type %s, source ip 10.0.0.1, destination ip 10.0.0.2", pkt_ethernet.ethertype)
        else:
		pkt = packet.Packet()
		pkt.add_protocol(ethernet.ethernet(ethertype=pkt_ethernet.ethertype,
                                           dst=pkt_ethernet.src,
                                           src='00:00:00:00:00:01'))
		pkt.add_protocol(arp.arp(opcode=arp.ARP_REPLY,
                                 src_mac='00:00:00:00:00:01',
                                 src_ip='10.0.0.1',
                                 dst_mac=pkt_arp.src_mac,
                                 dst_ip=pkt_arp.src_ip))
		action1 = [parser.OFPActionOutput(port=2)]
                action2=  [parser.OFPActionOutput(port=1)]
                self.add_flow((self.s1), 1 , '00:00:00:00:00:02','10.0.0.1','10.0.0.2', action1)
                self.add_flow((self.s1), 2,'00:00:00:00:00:01','10.0.0.2','10.0.0.1', action2)
                self.add_flow((self.s2), 1,'00:00:00:00:00:01','10.0.0.2','10.0.0.1', action1)
                self.add_flow((self.s2), 2,'00:00:00:00:00:02','10.0.0.1','10.0.0.2', action2)

        pkt.serialize()
        self._send_packet(datapath, port, pkt)
			
    def _send_packet(self, datapath, port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        self.logger.info("packet-out %s" % (pkt,))
        data = pkt.data
        actions = [parser.OFPActionOutput(port=port)]
        out = parser.OFPPacketOut(datapath=datapath,
                               buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER,
                                  actions=actions,
                                  data=data)
        datapath.send_msg(out)
