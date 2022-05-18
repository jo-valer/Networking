# Networking
Softwarized and virtualized mobile networks (aka Networking II) group project's repository.

### Morphing network slices

• GOAL: to enable RYU SDN controller to build network slices and dynamically modify their topology

• To consider that each network node might host«services», that in this case will be represented by virtual switches/routers

• The SDN controller will not only slice but reprogram connectivity within the slice

### Launch
````
ryu-manager dynamic_slicing.py &
sudo python3 network.py
````
### Shut down network
````
exit
sudo mn -c
````
### Commands
````
nodes // Available nodes
links // Show links
dump // process ID in linux and eth address
h1 ifconfig 
h1 ls // working directory
h1 ping -c3 h4 // ping 3 packets
dpctl dump-flows // show flow tables
iperf h1 h2 // testing TCP bandwidth between h1 and h2
````





