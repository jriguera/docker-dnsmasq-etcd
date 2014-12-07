#!/bin/sh

if [ ! -d /var/run/dnsmasq ]; then
    mkdir /var/run/dnsmasq
fi

export ETCD_PORT=${ETCD_PORT:-4001}
export ETCD_HOST=${ETCD_HOST:-10.1.42.1}
exec /usr/sbin/dnsmasq --pid-file=/var/run/dnsmasq/dnsmasq.pid --keep-in-foreground --conf-file=/etc/dnsmasq.conf

