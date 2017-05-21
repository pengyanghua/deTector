from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
import random

'''
Written by Yang Ji
'''

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        cookie = msg.cookie
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dpid = datapath.id
        #self.logger.info("packet loss %s %s", dpid, in_port)
        if(cookie<10000):
            return

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return

        dst = eth.dst
        src = eth.src

        loss = cookie-10000
        random.seed(random.random())
	loss_test = random.randint(0,10000)
        #self.logger.info("packet loss test [dpid 0x%x inport %d] rate %d/10000 test %d", dpid, in_port, loss, loss_test)

        if(loss_test < loss):
            self.logger.info("packet loss test [dpid 0x%x inport %d] rate %d/10000 test %d", dpid, in_port, loss, loss_test)
            return 

        #self.logger.info("packet trans")
        pkt_ipv4 = pkt.get_protocol(ipv4.ipv4)
        ip_dst = pkt_ipv4.dst
        ip_ecn = (pkt_ipv4.tos)&0x3
        phy_port_out=0
        ips = ip_dst.split('.')
        pod = int(ips[1])
        lr  = int(ips[2])
        if_no = 0
        if dpid < 0x200 :
            # core, ip
            if_no = pod +1
        elif dpid < 0x300 :
            # aggr
            spod = (dpid&0xFF)/2
            if pod == spod:
                if_no = 1+lr
            else :
                if_no = 3+ ip_ecn%2
        else :
            if in_port <3 :
                if_no = 3+ ip_ecn/2
            else :
                if_no = 1

        #actions = [parser.OFPActionOutput(ofproto.OFPP_TABLE, 0)]
        actions = [parser.OFPActionOutput(if_no, 1000)]

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=data)
        datapath.send_msg(out)

