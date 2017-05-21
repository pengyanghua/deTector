from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.controller import dpset
from ryu.controller import ofp_event
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import icmp
from ryu.lib.packet import packet_utils
from ryu.lib.packet import ipv4

import random


'''
Written by Yang Ji
'''


class IcmpResp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(IcmpResp, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.hw_addr = '00:33:22:00:33:22'
        self.ip_addr = '10.25.25.25'

    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def datapath_handler(self, ev):
        if ev.enter:
            packet_in_mask = (1 << ev.dp.ofproto.OFPR_ACTION | 
                                1 << ev.dp.ofproto.OFPR_INVALID_TTL)
            port_status_mask = (1 << ev.dp.ofproto.OFPPR_ADD |
                                1 << ev.dp.ofproto.OFPPR_DELETE |
                                1 << ev.dp.ofproto.OFPPR_MODIFY)
            flow_removed_mask = (1 << ev.dp.ofproto.OFPRR_IDLE_TIMEOUT |
                                1 << ev.dp.ofproto.OFPRR_HARD_TIMEOUT |
                                1 << ev.dp.ofproto.OFPRR_DELETE)
            m = ev.dp.ofproto_parser.OFPSetAsync(
                     ev.dp, [7, 0], [port_status_mask, 0],
                     [flow_removed_mask, 0])
            #ev.dp.send_msg(m)
            self.logger.info('Set SW config for TTL error packet in. DPID=%d'%ev.dp.id)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        reason = msg.reason
        ofproto = datapath.ofproto
	dpid = datapath.id
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        #self.logger.info("packet-in %s" % (pkt,))
        pkt_ethernet = pkt.get_protocols(ethernet.ethernet)[0]
        if not pkt_ethernet:
            return

        if pkt_ethernet.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return

        if reason != ofproto.OFPR_INVALID_TTL:
            #self.logger.info("INVALID TTL %s" % (pkt))
            # self.logger.info("INVALID TTL")
            if(msg.cookie<10000):
            	return
            dst = pkt_ethernet.dst
            src = pkt_ethernet.src
            loss = msg.cookie-10000
            random.seed(random.random())
	    loss_test = random.randint(0,10000)
            pkt_ipv4 = pkt.get_protocol(ipv4.ipv4)
            pkt_icmp = pkt.get_protocol(icmp.icmp)
            if(loss_test < loss):
                if pkt_icmp:		# only print icmp pkt loss
                    self.logger.info("packet loss test [dpid 0x%x inport %d] rate %d/10000 test %d", dpid, in_port, loss, loss_test)
                    return 
            
            if pkt_icmp:
                ip_dst = pkt_ipv4.dst
                ip_ecn = (pkt_icmp.type-20)&0x3
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
                actions = [parser.OFPActionOutput(if_no, 1000)]
                data = None
                if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                    data = msg.data
                out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=data)
                datapath.send_msg(out)

            return 

        pkt_ipv4 = pkt.get_protocol(ipv4.ipv4)
        pkt_icmp = pkt.get_protocol(icmp.icmp)
        if pkt_icmp:
            self._handle_icmp(datapath, in_port, pkt_ethernet, pkt_ipv4, pkt_icmp)
            return

    def _handle_icmp(self, datapath, port, pkt_ethernet, pkt_ipv4, pkt_icmp):
        pkt = packet.Packet()
        pkt.add_protocol(ethernet.ethernet(ethertype=pkt_ethernet.ethertype, dst=pkt_ethernet.src,src=self.hw_addr))
        pkt.add_protocol(ipv4.ipv4(dst=pkt_ipv4.src,src=self.ip_addr,proto=pkt_ipv4.proto))
        dpid = datapath.id
        #pkt.add_protocol(icmp.icmp(type_=icmp.ICMP_TIME_EXCEEDED,
        pkt.add_protocol(icmp.icmp(type_=icmp.ICMP_TIME_EXCEEDED,code=(10*dpid/256 +dpid%256),csum=0))
        self.logger.info("packet-in 0x%x, %d" %(dpid,(10*dpid/256+dpid%256)))
        #pkt.add_protocol(icmp.icmp(type_=icmp.ICMP_ECHO_REPLY,code=icmp.ICMP_ECHO_REPLY_CODE,csum=0))
        self._send_packet(datapath, port, pkt)

    def _send_packet(self, datapath, port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt.serialize()
        self.logger.info("packet-out TTL exceeded")
        data = pkt.data
        actions = [parser.OFPActionOutput(port=port)]
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER,
                                  actions=actions,
                                  data=data)
        datapath.send_msg(out)

