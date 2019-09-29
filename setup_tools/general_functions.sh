#!/usr/bin/env bash


BLUE="\e[34m"
RESET="\e[0m"

announce_section () {
    # Makes sections easier to see in output
    SECTION_BRK="\n==============================\n"
    SECTION="${1}"
    printf "${BLUE}${SECTION_BRK}${SECTION}${SECTION_BRK}${RESET}"
}

contains () {
    # Checks if the variable ($2) is in the space-separated list provided ($1)
    LIST=$1
    VAR=$2
    [[ "${LIST}" =~ (^|[[:space:]])"${VAR}"($|[[:space:]]) ]];
}

# This is to introduce a "do nothing" option to this script if it's run on its own
main () {
    contains "hello hi" "greetings"

}

# This is just like `if name == __main__` in python
if [[ "$1" != "--source-only" ]]; then
    main "${@}"
fi
