#!/bin/sh

if [ ! -z "$CONFD_BIN" ] && [ -x "$CONFD_BIN" ]; then
   ETCD_PORT=${ETCD_PORT:-4001}
   ETCD_HOST=${ETCD_HOST:-10.1.42.1}

   # Run confd in the background to watch the upstream servers
   exec $CONFD_BIN -node "http://$ETCD_HOST:$ETCD_PORT"
fi
exec true
