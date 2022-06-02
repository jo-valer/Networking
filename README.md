# Networking 2021/2022
This is the _Softwarized and virtualized mobile networks_ (aka _Networking II_) group project's repository by Daniele Della Pietra, Matteo Mazzonelli, and Giovanni Valer.

ℹ We have implemented two different scenarios, each with its own topology and simulations.

## 📁 <a href="https://github.com/jo-valer/Networking/tree/main/scenario_1">`1st scenario`</a><br>

<img src="https://github.com/jo-valer/Networking/blob/main/scenario_1.png" width="100%" height="100%"><br>

## 📁 <a href="https://github.com/jo-valer/Networking/tree/main/scenario_2">`2nd scenario`</a><br>

<img src="https://github.com/jo-valer/Networking/blob/main/scenario_2.png" width="100%" height="100%"><br>

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





