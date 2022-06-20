# `2nd scenario`

### ▶️ Demo
Launch network:
  ```
  ./run_controllers.sh
  ```
  ```
  sudo python3 network.py
  ```

**Test reachability**:
  ```
  pingall
  ```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_2/images/pingall.jpg" width="40%" height="40%"><br>

Use command ```dpctl dump-flows``` in order to check packets' flow from _h1_ to _h10_ through connecting slice (switch _s6_):
  ```
  dpctl dump-flows
  ```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_2/images/ping_h1_h10.jpg" width="120%" height="120%"><br>

Send UDP packets from _slice 3_ to _slice 1_:
  ```
  h1 iperf -s -u &
  ```
Repeat following command to see how UDP packets are discarded:
  ```
  h10 iperf -c 10.0.0.1 -u -t 5 -i 1 -l 300
  ```
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_2/images/test_UDP.jpg" width="50%" height="50%"><br>
After a certain amount of UDP packets transmitted, **switch _s6_ stops UDP connection** between _slice 1_ and _slice 3_. This event **doesn't affect TCP and ICMP packets' flows**.

Every 60 seconds UDP connections are restored and packets' counters are reset:
<br><img src="https://github.com/jo-valer/Networking/blob/main/scenario_2/images/reset_counter.jpg" width="50%" height="50%"><br>

### Shut down network
`mininet> exit`

`$ sudo mn -c`
