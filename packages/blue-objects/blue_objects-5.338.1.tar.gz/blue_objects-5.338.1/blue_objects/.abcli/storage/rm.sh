#! /usr/bin/env bash

function abcli_storage_rm() {
    local options=$1
    local do_dryrun=$(abcli_option_int "$options" dryrun 1)

    local object_name=$(abcli_clarify_object $2 void)

    abcli_eval dryrun=$do_dryrun \
        rm -rfv $ABCLI_OBJECT_ROOT/$object_name
}
