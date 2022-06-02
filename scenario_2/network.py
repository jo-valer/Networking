#!/usr/bin/python3

from re import I
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink


class NetworkSlicingTopo(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)
        
        # Create template host, switch, and link
        host_config = dict(inNamespace=True)
        host_link_config = dict(bw = 10)
        http_link_config = dict()
        

        # Create host nodes
        
        for i in range(6):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), **sconfig)

        # Create host nodes
        
        for i in range(13):
            self.addHost("h%d" % (i + 1), **host_config)
        # Add switch links
        self.addLink("s1", "s2", **http_link_config)
        self.addLink("s2", "s3", **http_link_config)
        self.addLink("s3", "s4", **http_link_config)
        self.addLink("s4", "s5", **http_link_config)
        self.addLink("s1", "s6", **http_link_config)
        self.addLink("s3", "s6", **http_link_config)
        self.addLink("s5", "s6", **http_link_config)

        # Add host links
        self.addLink("h1", "s1", **host_link_config)
        self.addLink("h2", "s1", **host_link_config)
        self.addLink("h3", "s2", **host_link_config)
        self.addLink("h4", "s1", **host_link_config)
        self.addLink("h5", "s2", **host_link_config)
        self.addLink("h6", "s3", **host_link_config)
        self.addLink("h7", "s4", **host_link_config)
        self.addLink("h8", "s3", **host_link_config)
        self.addLink("h9", "s4", **host_link_config)
        self.addLink("h10", "s5", **host_link_config)
        self.addLink("h11", "s5", **host_link_config)
        self.addLink("h12", "s5", **host_link_config)
        self.addLink("h13", "s6", **host_link_config)



topos = {"networkslicingtopo": (lambda: NetworkSlicingTopo())}

if __name__ == "__main__":
    topo = NetworkSlicingTopo()
    net = Mininet(
        topo=topo,
        controller = RemoteController("c0", ip="127.0.0.1"),
        switch=OVSKernelSwitch,
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )
    net.build()
    net.start()
    net['s1'].cmd("ovs-vsctl set-controller s1 tcp:127.0.0.1:6633")
    net['s1'].cmd("ovs-vsctl set-controller s2 tcp:127.0.0.1:6633 tcp:127.0.0.1:6634")
    net['s1'].cmd("ovs-vsctl set-controller s3 tcp:127.0.0.1:6634")
    net['s1'].cmd("ovs-vsctl set-controller s4 tcp:127.0.0.1:6634 tcp:127.0.0.1:6635")
    net['s1'].cmd("ovs-vsctl set-controller s5 tcp:127.0.0.1:6635")
    net['s1'].cmd("ovs-vsctl set-controller s6 tcp:127.0.0.1:6636")
    CLI(net)
    net.stop()
