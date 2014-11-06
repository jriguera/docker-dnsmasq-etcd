#!/bin/bash -e

if [ ! -z "$CONFD_BIN" ] && [ -x "$CONFD_BIN" ]; then
   # Loop until confd has updated the configs
   until $CONFD_BIN -onetime; do
      sleep 2
   done
fi

