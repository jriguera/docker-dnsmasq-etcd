#!/bin/bash -e

if [ ! -z "$CONFD_BIN" ] && [ -x "$CONFD_BIN" ]; then
   ETCD_PORT=${ETCD_PORT:-4001}
   ETCD_HOST=${ETCD_HOST:-10.1.42.1}

   # Loop until confd has updated the configs
   until $CONFD_BIN -onetime -node "http://$ETCD_HOST:$ETCD_PORT"; do
      sleep 2
   done
fi

