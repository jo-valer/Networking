# Networking
Softwarized and virtualized mobile networks (aka Networking II) group project's repository.

### Network Slice Setup Optimization

• GOAL: GOAL: to enable RYU SDN controller to slice the network and then to dynamically re-allocate services in order to maintain desired QoS

• Example 1: migrate a server to maximize throughtput via northbound script

• Example 2: migrate a server to minimize delay via northbound script
### Launch
````
ryu-manager slice1.py &
sudo python3 network.py
````
### Shut down network
````
exit
sudo mn -c
````



