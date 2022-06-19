# `1st scenario`

### ▶️ Demo
Launch network:
  ```
  ryu-manager dynamic_slicing.py & sudo python3 network.py
  ```

👉 **WHEN SWITCH 4 IS ON:**

**Test reachability**:
  ```
  h1 ping -c1 h2
  ```
  
  ```
  h1 ping -c1 h4
  ```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/pingall_ON.jpg" width="40%" height="40%"><br>


Use command ```dpctl dump-flows``` to show the flow tables:

  ```
  dpctl dump-flows
  ```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/h4_h5_ON.jpg" width="120%" height="120%"><br>
Notice that _h4_ communicates with _h5_ through switch _s4_


**Test bandwidth** of slices:
  ```
  iperf h1 h2
  ```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/bandwidth_ON.jpg" width="50%" height="50%"><br>


👉 **WHEN SWITCH 4 IS UNREACHABLE:**

Let's use the same commands after event: **'Switch 4 – OFF'**

**Test reachability**:
  ```
  h4 ping -c1 h5
  ```
  
  ```
  h5 ping -c1 h2
  ```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/pingall_OFF.jpg" width="40%" height="40%"><br>
As we can see slicing is preserved, citizens don't have access to essential services slice, and vice versa.


Use command ```dpctl dump-flows``` to show the flow tables:

  ```
  dpctl dump-flows
  ```

<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/h4_h5_OFF.jpg" width="120%" height="120%"><br>
Notice that _h4_ communicates with _h5_ through citizens' slice:


**Test bandwidth** of slices:
  ```
  iperf
  ```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_1/images/bandwidth_OFF.jpg" width="50%" height="50%"><br>
80% of available bandwidth is used by essential services and 20% by citizens, just as desired.

### Shut down network
`mininet> exit`

`$ sudo mn -c`
