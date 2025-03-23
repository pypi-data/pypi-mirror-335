#! /usr/bin/env bash

function abcli_storage_exists() {
    python3 -m blue_objects.storage \
        exists \
        --object_name "$1" \
        "${@:2}"
}
