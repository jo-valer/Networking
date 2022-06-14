# Networking 2021/2022
This is the _Softwarized and virtualized mobile networks_ (aka _Networking II_) group project's repository by **Daniele Della Pietra**, **Matteo Mazzonelli**, and **Giovanni Valer**.

ℹ We have implemented two different scenarios, each with its own topology and simulations.

## 📁 <a href="https://github.com/jo-valer/Networking/tree/main/scenario_1">`1st scenario`</a>

Here we imagine having a city, whose network is divided in 2 slices: the first (from now on: _slice_1_) is dedicated to **citizens' traffic** while the second (_slice_2_) is dedicated to **essential services** (eg. police, hospital).

It might happen that a natural disaster, boycott, or accident leads to irreparable damages to a part of the network (let's imagine switch 4 unreachable).

In such a situation we would like to dynamically change the slices, in order to have _slice_1_ overlaying _slice_2_, an so allowing communication between _h4_ and _h5_. Furthermore, we require that the available throughput of switch 2 is 80% dedicated to _slice_2_, since essential services could need even more capability in case of natural disaster.

### Key summary
- ✅ **Dynamical slices' morphing**
- ✅ **Essential services have 80% of dedicated throughput**

### 🖧 Topology

<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/topology_1.jpg" width="80%" height="80%"><br>

### ▶️ Demo
Launch network:
  ```
  ryu-manager dynamic_slicing.py & sudo python3 network.py
  ```
Test reachability by running ```mininet> pingall```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/pingall_ON.jpg" width="40%" height="40%"><br>


Use command ```dpctl dump-flows``` to show the flow tables. Notice that h4 communicates with h5 through switch s4
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/h4_h5_ON.jpg" width="120%" height="120%"><br>


Test bandwidth of slices with ```iperf```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/bandwidth_ON.jpg" width="50%" height="50%"><br>



Let's use the same commands after event: ```SWITCH 4 OFF```

Test reachability by running ```mininet> pingall```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/pingall_OFF.jpg" width="40%" height="40%"><br>
As we can see slicing is preserved, citizens can't communicate with essential service and vice versa


Use command ```dpctl dump-flows``` to show the flow tables. Notice that h4 communicates with h5 through citizens' slice
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/h4_h5_OFF.jpg" width="120%" height="120%"><br>


Test bandwidth of slices with ```iperf```: 80% of available bandwidth is used by essential services and 20% by citizens
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/bandwidth_OFF.jpg" width="50%" height="50%"><br>

### Shut down network
````
exit
sudo mn -c
````

## 📁 <a href="https://github.com/jo-valer/Networking/tree/main/scenario_2">`2nd scenario`</a>

In this second scenario we have the network of a classroom. When students work on group projects, the different goups can't communicate "_too much_". So there are three slices which are interconnected by a fourth one (let's assume it's the teacher).

Moreover, not every single packet is allowed to pass through _connect_slice_: in fact there is a maximum amount of UDP packets sendable between slices, and when the threshold is exceeded the UDP packets are discarded.


### Key summary
- ✅ **Connecting SDN slices**
- ✅ **Stateful packet filtering**: exceeding UDP packets are discarded

### 🖧 Topology

<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_2/images/topology_2.png" width="80%" height="80%"><br>

### ▶️ Demo
Launch network:
  ```
  ./run_controllers.sh & sudo python3 network.py
  ```
Test reachability by running ```mininet> pingall```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_2/images/pingall.jpg" width="40%" height="40%"><br>

Use command ```mininet> h1 ping h10``` and ```dpctl dump-flows``` in order to check that packet flow from h1 to h10 through the connecting slice (switch 6)
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_2/images/ping_h1_h10.jpg" width="120%" height="120%"><br>

Send UDP packets from slice 3 to slice 1:
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_2/images/test_UDP.jpg" width="50%" height="50%"><br>
After a certain amount of UDP packets transmitted, switch 6 stops UDP connection between slice 1 and slice 3. This event doesn't affect TCP and ICMP packets' flows.

Every 60 seconds UDP connections are restored and packets' counters are reset
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_2/images/reset_counter.jpg" width="50%" height="50%"><br>

### Shut down network
````
exit
sudo mn -c
````





