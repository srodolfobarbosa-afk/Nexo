#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
THIS SCRIPT PREPARES INSTRUCTIONS FOR PURGING SENSITIVE FILES FROM GIT HISTORY.
It DOES NOT perform force-push automatically. Run the commands below as a maintainer
with rights to force-push the repo. Review carefully before executing.
EOF

SENSITIVE=(".secrets.baseline" ".secrets.current" "nexo_data.db" "memoria_curto_prazo.json")

echo "Files to remove from history: ${SENSITIVE[*]}"

cat <<'EOF'
Recommended steps (run in a safe environment):

pip install --user git-filter-repo

# Mirror clone
git clone --mirror https://github.com/SEU-USER/Nexo.git
cd Nexo.git

# Example: remove paths
git filter-repo --invert-paths --path .secrets.baseline --path .secrets.current --path nexo_data.db --path memoria_curto_prazo.json

# Expire reflog and garbage collect
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push cleaned mirror
git push --force

EOF

echo "Purge script generated. Review and run the steps manually as repo admin."
