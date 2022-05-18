from re import sub
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.topology import event,switches
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.lib.mac import haddr_to_bin
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, ofproto_v1_3_parser
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import udp
from ryu.lib.packet import tcp
from ryu.lib.packet import icmp
import threading
import time
import copy
import subprocess


class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    hosts=["00:00:00:00:00:01","00:00:00:00:00:02","00:00:00:00:00:03","00:00:00:00:00:04","00:00:00:00:00:05"]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.exchange = False
        self.host_slice1 = ["00:00:00:00:00:01","00:00:00:00:00:02","00:00:00:00:00:03"] 
        self.host_slice2 = ["00:00:00:00:00:04","00:00:00:00:00:05"] 
        self.mac_to_port = {
            1: {"00:00:00:00:00:04":4, "00:00:00:00:00:05":1},
            2: {"00:00:00:00:00:02":3},
            3: {"00:00:00:00:00:04":1, "00:00:00:00:00:05":4},
        }
        self.mac_to_port_backup = {
            1: {"00:00:00:00:00:04":4, "00:00:00:00:00:05":1},
            2: {"00:00:00:00:00:02":3},
            3: {"00:00:00:00:00:04":1, "00:00:00:00:00:05":4},
        }

        self.slice_to_port = {
            1: {3:1, 2:4, 1:3, 4:2},
            3: {1:3, 2:4, 3:1, 4:2}
        }
        self.end_switches = [1, 3]
        self.datapath_list = [] 
        self.on_off = True
        self.thread_on_off = threading.Thread(target = self.turn_on_off_switch,args=(),daemon=True)
        self.thread_on_off.start()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install the table-miss flow entry.
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
        datapath.send_msg(mod)

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
        if (self.on_off is False and dpid == 4) or (dst in self.host_slice2 and src in self.host_slice1) or (dst in self.host_slice1 and src in self.host_slice2):
            return
        self.mac_to_port.setdefault(dpid, {})

       # self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.match["in_port"]

        out_port = 0

        if dpid in self.end_switches:
            # Allowing packet in slice2 to move through slice1 
            if self.on_off is False and dst in self.mac_to_port[dpid] and src in self.host_slice2:
                out_port = self.mac_to_port[dpid][dst]
            else:
                out_port = self.slice_to_port[dpid][msg.match["in_port"]]
        elif dpid in self.mac_to_port:
            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
            else:
                out_port = ofproto.OFPP_FLOOD
        else:
            out_port = ofproto.OFPP_FLOOD

        # install a flow to avoid packet_in next time
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        if out_port != ofproto.OFPP_FLOOD and out_port != 0 and dst in self.hosts and src in self.hosts:
            if self.on_off is True and dpid in self.end_switches:
                # slice flow entry: port to port 
                match = datapath.ofproto_parser.OFPMatch(in_port = msg.match["in_port"])
                self.add_flow(datapath, 1, match, actions)
            else:
                match = datapath.ofproto_parser.OFPMatch(eth_src=src,eth_dst=dst)
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.match["in_port"],
            actions=actions, data=data)
        datapath.send_msg(out)

        if out_port!=0:
           # self.logger.info("LOG s%s sending packet (out_port=%s)", dpid, out_port)
            datapath.send_msg(out)


    @set_ev_cls(event.EventSwitchEnter)
    def switch_enter_handler(self, ev):
        switch_dp = ev.switch.dp
        switch_dpid = switch_dp.id
        self.logger.info(f"Switch has been plugged in PID: {switch_dpid}")
        self.datapath_list.append(switch_dp)
        if len(self.datapath_list)==4:
            subprocess.call("./create_queues.sh")

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
            time.sleep(60)
            # Remove flow entries from every switch 
            for dp in self.datapath_list:
                self.remove_flows(dp,0)
            self.logger.info("Flow tables deleted")

            if self.on_off:
                self.logger.info("Switch 4 - OFF")
                subprocess.call("./flow_entries_queues.sh")
            else:
                self.logger.info("Switch 4 - ON")
            self.on_off = False if self.on_off is True else True
            # Because of new topology, reset mac_to_port  
            self.mac_to_port = copy.deepcopy(self.mac_to_port_backup)   
    
    def remove_flows(self, datapath, table_id):
        # Removing all flow entries
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        empty_match = parser.OFPMatch()
        instructions = []
        flow_mod = self.remove_table_flows(datapath, table_id,empty_match, instructions)
        datapath.send_msg(flow_mod)
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)
    

    def remove_table_flows(self, datapath, table_id, match, instructions):
        ofproto = datapath.ofproto
        flow_mod = datapath.ofproto_parser.OFPFlowMod(datapath, 0, 0, table_id,
                                                      ofproto.OFPFC_DELETE, 0, 0,
                                                      1,
                                                      ofproto.OFPCML_NO_BUFFER,
                                                      ofproto.OFPP_ANY,
                                                      ofproto.OFPG_ANY, 0,
                                                      match, instructions)    
        return flow_mod