#!/usr/bin/env bash
# Alle Tests gegen die simulierte Companion ausführen.
# Seite wählen: MCW_PAGE=beta/index.html ./run_tests.sh   (Standard: index.html)
set -u
cd "$(dirname "$0")"
fail=0
for t in test_*.py; do
  echo "::group::$t"
  if timeout 300 python3 "$t"; then echo "✓ $t"; else echo "✗ $t"; fail=1; fi
  echo "::endgroup::"
done
exit $fail
