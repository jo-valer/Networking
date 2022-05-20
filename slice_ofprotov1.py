from pickle import FALSE
from ssl import OP_ENABLE_MIDDLEBOX_COMPAT
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.topology import event,switches
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0, ofproto_v1_0_parser
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
import threading
import time
import copy


class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
    hosts=["00:00:00:00:00:01","00:00:00:00:00:02","00:00:00:00:00:03","00:00:00:00:00:04","00:00:00:00:00:05","00:00:00:00:00:06","00:00:00:00:00:07"]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.exchange = False
        self.host_slice1_right = ["00:00:00:00:00:02","00:00:00:00:00:03","00:00:00:00:00:04"]
        self.host_slice1_left = ["00:00:00:00:00:01","00:00:00:00:00:02","00:00:00:00:00:03"] 
        self.host_slice2 = ["00:00:00:00:00:05","00:00:00:00:00:06","00:00:00:00:00:07"] 
        self.mac_to_port = {
            1: {"00:00:00:00:00:05":4, "00:00:00:00:00:07":1},
            3: {"00:00:00:00:00:05":1, "00:00:00:00:00:07":4},
        }
        self.mac_to_port_backup = {
            1: {"00:00:00:00:00:05":4, "00:00:00:00:00:07":1},
            3: {"00:00:00:00:00:05":1, "00:00:00:00:00:07":4},
        }

        self.slice_to_port = {
            1: {3:1, 2:4, 1:3, 4:2},
            3: {1:3, 2:4, 3:1, 4:2}
        }
        self.end_switches = [1, 3]
        self.switches = []
        self.datapath_list = [] 
        self.rx_bytes = {}
        self.on_off = True
        self.thread_on_off = threading.Thread(target = self.turn_on_off_switch,args=(),daemon=True)
        self.thread_on_off.start()

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

    # This function not used right now 
    def run_check(self, ofp_parser, switch_dp):
        threading.Timer(60, self.run_check, args=(ofp_parser, switch_dp)).start()
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
        dp_id = ev.msg.datapath.id
        oldrx = self.rx_bytes[dp_id]
        self.rx_bytes[dp_id] = 0
        for stat in body:
            self.rx_bytes[dp_id] += stat.rx_bytes

        traffic = self.rx_bytes[dp_id] - oldrx
       # print("Traffic monitoring across switch",dp_id,"=",traffic,"bytes")
       # print("---------------------------------")


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

        # Switch 4 is off, packets are dropped 
        if self.on_off is False and dpid == 4:
            return
        self.mac_to_port.setdefault(dpid, {})

       # self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.in_port

        out_port = 0

        if dpid in self.end_switches:
            if self.on_off is False and dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
            else:
                out_port = self.slice_to_port[dpid][msg.in_port]
        elif dpid in self.mac_to_port:
            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
            else:
                out_port = ofproto.OFPP_FLOOD
        else:
            out_port = ofproto.OFPP_FLOOD

        # Deciding if queue is necessary 
        if dpid == 1 and self.on_off is False:
            if dst in self.host_slice1_right:
                actions = [datapath.ofproto_parser.OFPActionEnqueue(out_port,123)]
            elif dst == "00:00:00:00:00:07":        
                actions = [datapath.ofproto_parser.OFPActionEnqueue(out_port,234)]
            else:
                actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        elif dpid == 3 and self.on_off is False:
            if dst in self.host_slice1_left:
                actions = [datapath.ofproto_parser.OFPActionEnqueue(out_port,123)]
            elif dst == "00:00:00:00:00:05":        
                actions = [datapath.ofproto_parser.OFPActionEnqueue(out_port,234)]
            else:
                actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        else:
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
            self.rx_bytes[switch_dpid] = 0
            if(switch_dpid == 2 or switch_dpid == 4 ):
                self.switches.append(switch_dpid)
                self.run_check(ofp_parser, switch_dp)
            self.datapath_list.append(switch_dp)

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

    def turn_on_off_switch(self):
        # Switch 4 ON-OFF every 60 seconds  
        while True:
            time.sleep(360)
            if self.on_off:
                print("Switch 4 - OFF")
            else:
                print("Switch 4 - ON")
            self.on_off = False if self.on_off is True else True
            # Remove flow entries of every switch 
            for dp in self.datapath_list:
                self.send_queue_stats_request(dp)
                self.remove_flows(dp,0)
            
            # Because of new topology, reset mac_to_port  
            self.mac_to_port = copy.deepcopy(self.mac_to_port_backup)   
            print("Flow tables deleted")
    
    def remove_flows(self, datapath, table_id):
        """Removing all flow entries."""
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        empty_match = parser.OFPMatch()
        instructions = []
        flow_mod = self.remove_table_flows(datapath, table_id,
                                        empty_match, instructions)
        datapath.send_msg(flow_mod)
    

    def remove_table_flows(self, datapath, table_id, match, instructions):
        """Create OFP flow mod message to remove flows from table."""
        ofproto = datapath.ofproto
        flow_mod = datapath.ofproto_parser.OFPFlowMod(datapath,match,0,ofproto.OFPFC_DELETE,0,0,1,ofproto.OFP_NO_BUFFER,ofproto.OFPP_NONE,0,instructions)
        return flow_mod

    def send_queue_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPQueueStatsRequest(datapath, 0, ofp.OFPP_NONE,
                                            ofp.OFPQ_ALL)
        datapath.send_msg(req)
    @set_ev_cls(ofp_event.EventOFPQueueStatsReply, MAIN_DISPATCHER)
    def stats_reply_handler(self, ev):
        msg = ev.msg
        body = ev.msg.body
        for stat in body:
            print("QUEUE ID: ", stat.queue_id," --- PORT NUMBER: ",stat.port_no)
        