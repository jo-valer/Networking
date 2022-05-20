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

        

        # Create host nodes
        
        for i in range(5):
            self.addHost("h%d" % (i + 1), **host_config)
      
        # Add host links
        self.addLink("h1", "h2", **host_link_config)
        self.addLink("h1", "h3", **host_link_config)
        self.addLink("h1", "h4", **host_link_config)
        self.addLink("h1", "h5", **host_link_config)

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
    CLI(net)
    net.stop()
