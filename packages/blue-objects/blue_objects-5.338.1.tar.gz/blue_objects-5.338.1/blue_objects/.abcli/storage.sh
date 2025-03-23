#! /usr/bin/env bash

function abcli_storage() {
    local task=$(abcli_unpack_keyword $1 void)

    local function_name=abcli_storage_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    python3 -m blue_objects.storage "$@"
}

abcli_source_caller_suffix_path /storage
