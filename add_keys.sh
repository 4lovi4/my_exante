#!/bin/bash
#SSH-ADD my favourite keys 
declare -a KEYS_LIST
KEYS_LIST=( "id_rsa" "buck_ssh.key" )
for KEY in ${KEYS_LIST[*]}; do
    ssh-add "${HOME}/.ssh/$KEY"
done
exit 0

