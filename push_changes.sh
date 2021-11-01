#!/usr/bin/env bash
# Calls the push_changes file at whatever path the py-package-manager repo is in
PPM_PATH=../extras/py-package-manager/push_changes.sh
if [[ ! -f "${PPM_PATH}" ]]
then
    # The newer method is to bring kavalkilu into the same directory with the other projects
    PPM_PATH=../py-package-manager/push_changes.sh
fi

if [[ ! -z "${PPM_PATH}" ]]
then
  ADDL="${@}" # Option for passing additional commands onwards
  sh ${PPM_PATH} --config ./config.py ${ADDL}
else
  echo -e "The py-package-manager repo is not in the expected path: ${PPM_PATH}\nAborting process..." && exit 1
fi
