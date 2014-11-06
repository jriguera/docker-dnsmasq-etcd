#!/bin/bash -e

if [ ! -z "$CONFD_BIN" ] && [ -x "$CONFD_BIN" ]; then
   # Run confd in the background to watch the upstream servers
   /usr/bin/confd
fi

