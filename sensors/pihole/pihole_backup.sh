#!/usr/bin/env bash
# PIHOLE BACKUP
# ==========================================
#   Create a backup of pihole-FTL.db

# Function to add timestamp before entry
adddate() {
    while IFS= read -r line; do
        echo "$(date +"%Y-%m-%d %H:%M:%S") :: $line" 1>&2
    done
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
echo "This goes to ${log_path}" | adddate
echo "This goes to ${log_path} too" | adddate


# Print a message to the original standard output (e.g. terminal)
#echo "This goes to the original stdout" 1>&3

# Prep backup
echo "Backing up db at ${db_path} to backup at ${backup_path}" | adddate
# Backup
sqlite3 ${db_path} ".backup ${backup_path}" && echo "Backup complete" | adddate

echo "Finished process. Exiting \n =====" | adddate

# Restore original stdout/stderr
exec 1>&3 2>&4
# Close the unused descriptors
exec 3>&- 4>&-

