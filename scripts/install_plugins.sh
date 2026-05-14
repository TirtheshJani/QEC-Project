#!/usr/bin/env bash
# Install the three Claude Code plugins this project depends on.
#
# Idempotent: re-run safely. Plugins are external; this script does NOT vendor
# any files into the repo. License compliance: ARS is CC-BY-NC 4.0, Superpowers
# and Scientific Agent Skills are MIT-equivalent — we install, never copy.
#
# Usage:
#   bash scripts/install_plugins.sh
#
# The /plugin commands must be pasted into a Claude Code session in this repo.
# This script prints them and (if available) runs the npx-based install.

set -euo pipefail

cat <<'EOF'
================================================================================
QEC-Project plugin install
================================================================================

Paste these into a Claude Code session inside this repository:

    /plugin install superpowers@claude-plugins-official
    /plugin marketplace add Imbad0202/academic-research-skills
    /plugin install academic-research-skills

If the official marketplace lookup fails for Superpowers, fall back to:

    /plugin marketplace add obra/superpowers-marketplace
    /plugin install superpowers@superpowers-marketplace

================================================================================
Scientific Agent Skills (no /plugin needed; uses npx)
================================================================================
EOF

if command -v npx >/dev/null 2>&1; then
    echo "Running: npx skills add K-Dense-AI/scientific-agent-skills"
    npx --yes skills add K-Dense-AI/scientific-agent-skills || {
        echo
        echo "  npx invocation failed. You can also clone manually:"
        echo "    git clone https://github.com/K-Dense-AI/scientific-agent-skills.git ~/scientific-agent-skills"
        echo
    }
else
    cat <<'EOF'
npx not found on PATH. Install Node.js (https://nodejs.org/) then run:

    npx skills add K-Dense-AI/scientific-agent-skills

Or clone directly:

    git clone https://github.com/K-Dense-AI/scientific-agent-skills.git ~/scientific-agent-skills

EOF
fi

cat <<'EOF'
================================================================================
Done. Verify inside Claude Code:
  /plugin                  # should list superpowers + academic-research-skills
  /ars-plan                # should be recognized
EOF
