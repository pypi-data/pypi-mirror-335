#! /usr/bin/env bash

function abcli_storage_list() {
    python3 -m blue_objects.storage \
        list_of_objects \
        --prefix "$1" \
        "${@:2}"
}
