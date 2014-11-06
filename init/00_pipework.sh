#!/bin/bash -e

if [ ! -z "$PIPEWORK_BIN" ] && [ -x "$PIPEWORK_BIN" ]; then
  /usr/bin/pipework --wait
fi
