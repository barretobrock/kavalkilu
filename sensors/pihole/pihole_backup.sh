#!/usr/bin/env bash
# PIHOLE BACKUP
# ==========================================
#   Create a backup of pihole-FTL.db

# Set logging things
declare -A levels=([DEBUG]=0 [INFO]=1 [WARN]=2 [ERROR]=3)
log_name="pihole_backup"
script_logging_level="DEBUG"

logThis() {
    local log_message=$1
    local log_priority=$2

    #check if level exists
    [[ ${levels[$log_priority]} ]] || return 1

    #check if level is enough
    (( ${levels[$log_priority]} < ${levels[$script_logging_level]} )) && return 2

    #log here
    echo "$(date +"%Y-%m-%d %H:%M:%S") - ${log_name} - ${log_priority}   ${log_message}" 1>&2
}

now=$(date +"%Y%m%d")
db_path="/etc/pihole/pihole-FTL.db"
backup_path="$HOME/data/pihole-FTL.db.backup"
log_path="$HOME/logs/pihole_db/pihole_backup_$now.log"

# Save standard output and standard error
exec 3>&1 4>&2
# Redirect standard output and error to a log file
exec 1>${log_path}
# Redirect standard error to a log file
exec 2>${log_path}

# Now test output of all commands
logThis "This goes to ${log_path}" "DEBUG"
logThis "This goes to ${log_path} too" "DEBUG"

# Prep backup
logThis "Backing up db at ${db_path} to backup at ${backup_path}" "DEBUG"
# Backup
ERRCHECK="$(sqlite3 ${db_path} ".backup ${backup_path}" 2>&1)" && logThis "Backup complete" "DEBUG"

# Check if command successfully executed
if [[ $? -eq 0 ]]; then
    logThis "Command successfully executed." "DEBUG"
else
    logThis "There was an error: ${ERRCHECK}" "ERROR"
fi

logThis "Finished process. Exiting. \n =====" "DEBUG"

# Restore original stdout/stderr
exec 1>&3 2>&4
# Close the unused descriptors
exec 3>&- 4>&-
