#!/bin/bash

set -eu
set -o pipefail

DEBUG=${DEBUG:-0}
ROOTLESS=${ROOTLESS:-0}
PALAESTRAI_BIN=${PALAESTRAI_BIN:-$(which palaestrai)}
PALAESTRAI_USER=${PALAESTRAI_USER:-palaestrai}
PALAESTRAI_GROUP=${PALAESTRAI_GROUP:-palaestrai}
PALAESTRAI_UID=${PALAESTRAI_UID:-$(id -u palaestrai)}
PALAESTRAI_GID=${PALAESTRAI_GID:-$(id -g palaestrai)}
PALAESTRAI_RUNTIME_CONFIG=${PALAESTRAI_RUNTIME_CONFIG:-/workspace/palaestrai.conf}
SUDO=(sudo --preserve-env --set-home --user "${PALAESTRAI_USER}")

if [ $# -eq 0 ]; then
  command=(
    "$PALAESTRAI_BIN"
    -c "$PALAESTRAI_RUNTIME_CONFIG"
    experiment-start
    /workspace
  )
else
  # The arguments needs to be wrapped with bash for gitlab runner
  # pre shell identification script to work
  command=( "$@" )
fi

if [ "$ROOTLESS" -eq 1 ]; then
  SUDO=(sudo --preserve-env --set-home)
fi

cat <<'__EOF'

             _                 _               _____
            | |               | |        /\   |_   _|
 _ __   __ _| | __ _  ___  ___| |_ _ __ /  \    | |
| '_ \ / _` | |/ _` |/ _ \/ __| __| '__/ /\ \   | |
| |_) | (_| | | (_| |  __/\__ \ |_| | / ____ \ _| |_
| .__/ \__,_|_|\__,_|\___||___/\__|_|/_/    \_\_____|
| |
|_|

__EOF
cat <<__EOF

Current User:               $(whoami)
UID:                        $(id -u)
GID:                        $(id -g)
PALAESTRAI_USER:            ${PALAESTRAI_USER}
PALAESTRAI_GROUP:           ${PALAESTRAI_USER}
PALAESTRAI_UID:             ${PALAESTRAI_UID}
PALAESTRAI_GID:             ${PALAESTRAI_GID}
CWD:                        /workspace
PALAESTRAI_RUNTIME_CONFIG:  ${PALAESTRAI_RUNTIME_CONFIG}
SUDO:                       ${SUDO[*]}
PALAESTRAI_BIN:             $(which palaestrai)
Command:                    ${command[*]}
__EOF


[ "$DEBUG" -ne 0 ] && set -x

# Take care of potential renaming:

if [ "$(id -u)" -eq 0 ] && [ "$ROOTLESS" -ne 1 ]; then
  if [ "$PALAESTRAI_USER" != "palaestrai" ]; then
    echo -n "Renaming user \"palaestrai\" to \"$PALAESTRAI_USER\"... "
    usermod \
      --home "/home/${PALAESTRAI_USER}" \
      --move-home \
      --login "$PALAESTRAI_USER" \
      --uid "$PALAESTRAI_UID" \
      palaestrai
    echo "Ok."
  fi

  if [ "$PALAESTRAI_GROUP" != "palaestrai" ] \
      || [ "$PALAESTRAI_GID" \
        -ne "$(getent group "$PALAESTRAI_GROUP"|cut -d: -f3)" ]; then
    echo "Changing group \"palaestrai\" with GID " \
      "$(getent group "$PALAESTRAI_GROUP"|cut -d: -f3) " \
      " to \"$PALAESTRAI_GROUP\" with GID \"$PALAESTRAI_GID\"... "
      groupmod \
        --gid "$PALAESTRAI_GID" \
        --new-name "$PALAESTRAI_GROUP" \
        palaestrai
  fi

  if [ "$PALAESTRAI_GID" != "$(id -g "$PALAESTRAI_USER")" ]; then
      echo -n "Adding user \"$PALAESTRAI_USER\" to " \
        "group \"$PALAESTRAI_GROUP\" with GID \"$PALAESTRAI_GID\"... "
      usermod \
        --gid "$PALAESTRAI_GID" \
        "$PALAESTRAI_USER"
      echo "Ok."
  fi

  if [ "$(stat --printf='%u' /workspace)" -ne "$PALAESTRAI_UID" ]; then
    chown "$PALAESTRAI_UID" /workspace
  fi
  if [ "$(stat --printf='%g' /workspace)" -ne "$PALAESTRAI_GID" ]; then
    chgrp "$PALAESTRAI_GID" /workspace
  fi
fi

if [ ! -e "$PALAESTRAI_RUNTIME_CONFIG" ]; then
  echo "Creating default runtime configuration ${PALAESTRAI_RUNTIME_CONFIG}."
  palaestrai runtime-config-show-default > "$PALAESTRAI_RUNTIME_CONFIG"

  if [ "$(id -u)" -eq 0 ] && [ "$ROOTLESS" -ne 1 ]; then
    chown "$PALAESTRAI_UID":"$PALAESTRAI_GID" "$PALAESTRAI_RUNTIME_CONFIG"
  fi
fi

if [ -r /workspace/requirements.txt ]; then
  echo "Installing additional Python packages..."
  pip install -U --force-reinstall -r /workspace/requirements.txt
fi

echo
echo "Contents of /workspace:"
ls -lah /workspace

echo
echo "Current runtime configuration:"
eval "${SUDO[@]}" \
  PATH="${PATH}" \
  PYTHONPATH="${PYTHONPATH:-}" \
  XDG_CACHE_HOME="/home/${PALAESTRAI_USER}/.cache" \
  JOBLIB_TEMP_FOLDER='/tmp' \
  "$PALAESTRAI_BIN" -c "$PALAESTRAI_RUNTIME_CONFIG" \
  runtime-config-show-effective

echo
echo "Executing ${command[*]}..."
exec "${SUDO[@]}" \
  PATH="${PATH}" \
  PYTHONPATH="${PYTHONPATH:-}" \
  XDG_CACHE_HOME="/home/${PALAESTRAI_USER}/.cache" \
  JOBLIB_TEMP_FOLDER='/tmp' \
  "${command[@]}"
