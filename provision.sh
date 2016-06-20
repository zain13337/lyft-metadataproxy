#!/bin/bash
set -e
exec /sbin/iptables --wait -t nat \
                    -A PREROUTING \
                    -i docker0 \
                    -p tcp \
                    --dport 80 \
                    --destination 169.254.169.254 \
                    --jump DNAT \
                    --to-destination 172.17.0.1:45001
