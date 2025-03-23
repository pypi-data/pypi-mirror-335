#! /usr/bin/env bash

function abcli_storage_status() {
    local options=$1
    local count=$(abcli_option_int "$options" count 10)
    local depth=$(abcli_option_int "$options" depth 2)
    local do_dryrun=$(abcli_option_int "$options" dryrun 0)

    abcli_eval dryrun=$do_dryrun,path=$ABCLI_PATH_STORAGE \
        "du -hc -d $depth | sort -h -r | head -n $count"
}
