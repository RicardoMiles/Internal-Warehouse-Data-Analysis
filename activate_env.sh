# Use it like: source ./activate_env.sh

VENV_DIR="warelytic"   #  venv folder name
ACT="$VENV_DIR/bin/activate"

# Detect if sourced (works in bash/zsh)
is_sourced=0
( return 0 2>/dev/null ) && is_sourced=1
if [ $is_sourced -eq 0 ]; then
  echo "This script must be sourced. Run: source ./activate_env.sh"
  exit 1
fi

if [ ! -f "$ACT" ]; then
  echo "Not found: $ACT"
  return 1
fi

# Activate
. "$ACT"
echo "Activated: $VIRTUAL_ENV"
