#!/bin/sh

# Flow entries switch 1
sudo ovs-ofctl add-flow s1 ip,priority=2,nw_src=10.0.0.4,nw_dst=10.0.0.5,idle_timeout=0,actions=set_queue:234,normal
sudo ovs-ofctl add-flow s1 ip,priority=2,nw_src=10.0.0.1,nw_dst=10.0.0.2,idle_timeout=0,actions=set_queue:123,normal
sudo ovs-ofctl add-flow s1 ip,priority=2,nw_src=10.0.0.1,nw_dst=10.0.0.3,idle_timeout=0,actions=set_queue:123,normal

# Flow entries switch 2
sudo ovs-ofctl add-flow s2 ip,priority=2,nw_src=10.0.0.2,nw_dst=10.0.0.1,idle_timeout=0,actions=set_queue:123,normal
sudo ovs-ofctl add-flow s2 ip,priority=2,nw_src=10.0.0.2,nw_dst=10.0.0.3,idle_timeout=0,actions=set_queue:345,normal

# Flow entries switch 3
sudo ovs-ofctl add-flow s3 ip,priority=2,nw_src=10.0.0.3,nw_dst=10.0.0.1,idle_timeout=0,actions=set_queue:123,normal
sudo ovs-ofctl add-flow s3 ip,priority=2,nw_src=10.0.0.3,nw_dst=10.0.0.2,idle_timeout=0,actions=set_queue:123,normal
sudo ovs-ofctl add-flow s3 ip,priority=2,nw_src=10.0.0.5,nw_dst=10.0.0.4,idle_timeout=0,actions=set_queue:234,normal