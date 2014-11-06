#!/bin/bash -e

export ETCD_PORT=${ETCD_PORT:-4001}
export ETCD_HOST=${ETCD_HOST:-10.1.42.1}
export ETCD="http://$ETCD_HOST:$ETCD_PORT"

/etc/init.d/dnsmasq start
