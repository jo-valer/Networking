from pickle import FALSE
from ssl import OP_ENABLE_MIDDLEBOX_COMPAT
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.topology import event,switches
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0,ofproto_v1_0_parser
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
import threading
import os

class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    hosts=["00:00:00:00:00:01","00:00:00:00:00:02","00:00:00:00:00:03","00:00:00:00:00:04","00:00:00:00:00:05","00:00:00:00:00:06","00:00:00:00:00:07"]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.exchange = False
        self.mac_to_port = {}
        self.slice_to_port = {
            1: {3:1, 2:4, 1:3, 4:2},
            3: {1:3, 2:4, 3:1, 4:2}
        }
        self.end_switches = [1, 3]
        self.switches = []
        self.datapath_list = {}
        self.rx_bytes = {}

    def add_flow(self, datapath, in_port, dst, src, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port,
            dl_dst=haddr_to_bin(dst), dl_src=haddr_to_bin(src))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        datapath.send_msg(mod)

    def run_check(self, ofp_parser, switch_dp):
        threading.Timer(10.0, self.run_check, args=(ofp_parser, switch_dp)).start()
        
        if(switch_dp.id == 2):
            req = ofp_parser.OFPPortStatsRequest(switch_dp,0,switch_dp.ofproto.OFPP_NONE)
            switch_dp.send_msg(req)

        else:
            req = ofp_parser.OFPPortStatsRequest(switch_dp,0,switch_dp.ofproto.OFPP_NONE)
            switch_dp.send_msg(req)

            

       


    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body
        # self.logger.info('datapath         port     '
        #                  'rx-pkts  rx-bytes rx-error '
        #                  'tx-pkts  tx-bytes tx-error')
        # self.logger.info('---------------- -------- '
        #                  '-------- -------- -------- '
        #                  '-------- -------- --------')
        # for stat in body:
        #     self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
        #                      ev.msg.datapath.id, stat.port_no,
        #                      stat.rx_packets, stat.rx_bytes, stat.rx_errors,
        #                      stat.tx_packets, stat.tx_bytes, stat.tx_errors)
        oldrx = 0
        dp_id = ev.msg.datapath.id
        for stat in body:
            if stat.port_no == 1:
                oldrx = self.rx_bytes[dp_id]
                self.rx_bytes[dp_id] = 0
            self.rx_bytes[dp_id] += stat.rx_bytes

        traffic = self.rx_bytes[dp_id] - oldrx
        print("Traffic monitoring across switch",dp_id,"=",traffic,"bytes")
        print("---------------------------------")


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg

        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

       # self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.in_port

        out_port = 0

        # if (dpid == 1 and msg.in_port == 1 and dst != "00:00:00:00:00:01") or (dpid == 3 and msg.in_port == 1 and dst != "00:00:00:00:00:04"):
        #     return

        if dpid in self.end_switches:
           #qui mettiamo le cose 
            # if self.exchange:
            #     self.slice_to_port= {
            #         1: {3:1, 2:4, 1:3, 4:2},
            #         3: {1:3, 2:4, 3:1, 4:2}
            #     }
            # else:
            #     self.slice_to_port= {
            #         1: {3:1, 2:4, 1:3, 4:2},
            #         3: {1:3, 2:4, 3:1, 4:2}
            #     }
            out_port = self.slice_to_port[dpid][msg.in_port]
        elif dpid in self.mac_to_port:
            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
            else:
                out_port = ofproto.OFPP_FLOOD
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD and out_port != 0 and dst in self.hosts and src in self.hosts:
            self.add_flow(datapath, msg.in_port, dst, src, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=data)
        datapath.send_msg(out)

        if out_port!=0:
           # self.logger.info("LOG s%s sending packet (out_port=%s)", dpid, out_port)
            datapath.send_msg(out)


    @set_ev_cls(event.EventSwitchEnter)
    def switch_enter_handler(self, ev):
        switch_dp = ev.switch.dp
        switch_dpid = switch_dp.id
        ofp_parser = switch_dp.ofproto_parser

        self.logger.info(f"Switch has been plugged in PID: {switch_dpid}")

        if switch_dpid not in self.switches:
            self.datapath_list[switch_dpid] = switch_dp
            self.rx_bytes[switch_dpid] = 0
            if(switch_dpid == 2 or switch_dpid == 4 ):
                self.switches.append(switch_dpid)
                self.run_check(ofp_parser, switch_dp)
       # self.run_check(ofp_parser, switch_dp)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illegal port state %s %s", port_no, reason)
