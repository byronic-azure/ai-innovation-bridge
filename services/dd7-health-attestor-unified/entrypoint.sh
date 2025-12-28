#!/bin/sh
set -eu

impl="${DD7_ATTESTOR_IMPL:-go}"

case "$impl" in
  rust)
    exec /usr/local/bin/dd7-health-attestor-rust
    ;;
  go)
    exec /usr/local/bin/dd7-health-attestor-go
    ;;
  *)
    echo "DD7: invalid DD7_ATTESTOR_IMPL='$impl' (must be 'go' or 'rust')" >&2
    exit 2
    ;;
esac
