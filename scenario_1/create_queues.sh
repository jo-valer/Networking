#!/bin/sh

echo ' ---------------------------------------------- '
echo 'Switch 1: creating two queues on port 1:'
sudo ovs-vsctl set port s1-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:123=@1q \
queues:234=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=2000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=8000000 
echo ' '

echo 'Switch 2: creating two queues on port 1'
sudo ovs-vsctl set port s2-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:123=@1q \
queues:234=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=2000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=8000000 
echo ' '

echo 'Switch 2: creating two queues on port 2'
sudo ovs-vsctl set port s2-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:345=@1q \
queues:456=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=2000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=8000000 
echo ' '

echo 'Switch 3: creating two queues on port 1'
sudo ovs-vsctl set port s3-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:123=@1q \
queues:234=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=2000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=8000000 
echo '*** End of Creating the Queues...'
echo ' ---------------------------------------------- '

