#!/bin/bash -e

if [ ! -z "$PIPEWORK_BIN" ] && [ -x "$PIPEWORK_BIN" ]; then
  $PIPEWORK_BIN --wait
fi
