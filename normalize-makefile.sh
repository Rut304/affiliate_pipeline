#!/usr/bin/env bash
# normalize-makefile.sh — auto-heals whitespace/tab issues in Makefiles
# 1. Removes illegal tabs/spaces from directives & target labels
# 2. Forces real tabs on recipe lines
# 3. Strips non-printable control characters
# 4. Creates a backup before changes for audit traceability

set -euo pipefail

MF="Makefile"

if [[ ! -f "$MF" ]]; then
    echo "❌ $MF not found in current directory"
    exit 1
fi

# Backup original
cp "$MF" "$MF.bak_normalize"

awk '
  BEGIN { inrecipe=0 }
  # Any target line: reset state, print
  /^[^[:space:]].*:$/ {
      inrecipe=1
      gsub(/[^[:print:]\t]/,"")   # strip control chars
      print
      next
  }
  # End recipe block on blank line
  inrecipe && /^[[:space:]]*$/ {
      inrecipe=0
      print
      next
  }
  # First three lines: strip leading tabs/spaces (for directives/labels)
  NR<=3 {
      sub(/^[ \t]+/, "")
      gsub(/[^[:print:]\t]/,"")
      print
      next
  }
  # Recipe line: convert leading spaces to a tab, strip junk
  inrecipe {
      sub(/^[ ]+/, "\t")
      gsub(/[^[:print:]\t]/,"")
      print
      next
  }
  # All other lines: just strip non-printables
  {
      gsub(/[^[:print:]\t]/,"")
      print
  }
' "$MF.bak_normalize" > "$MF"

echo "✅ $MF normalized. Backup saved as $MF.bak_normalize"
