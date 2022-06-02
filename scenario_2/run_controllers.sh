#!/bin/bash

ryu-manager slice1.py --observe-links --ofp-tcp-listen-port 6633 &
ryu-manager slice2.py --observe-links --ofp-tcp-listen-port 6634 &
ryu-manager slice3.py --observe-links --ofp-tcp-listen-port 6635 &
ryu-manager connect_slice.py --observe-links --ofp-tcp-listen-port 6636 &