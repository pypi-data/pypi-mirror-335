#! /usr/bin/env bash

function test_blue_objects_help() {
    local options=$1

    # legacy, not tested:
    #  - @mysql

    local module
    for module in \
        "@assets" \
        "@assets publish" \
        \
        "@objects" \
        \
        "@objects pypi" \
        "@objects pypi browse" \
        "@objects pypi build" \
        "@objects pypi install" \
        \
        "@objects pytest" \
        \
        "@objects test" \
        "@objects test list" \
        \
        "@cp" \
        \
        "@download" \
        \
        "@gif" \
        \
        "@host" \
        "@host get" \
        "@host reboot" \
        "@host shutdown" \
        \
        "@metadata" \
        "@metadata get" \
        "@metadata post" \
        \
        "@mlflow" \
        "@mlflow browse" \
        "@mlflow cache" \
        "@mlflow get_id" \
        "@mlflow get_run_id" \
        "@mlflow list_registered_models" \
        "@mlflow log_artifacts" \
        "@mlflow log_run" \
        "@mlflow rm" \
        "@mlflow run" \
        "@mlflow tags" \
        "@mlflow tags clone" \
        "@mlflow tags get" \
        "@mlflow tags search" \
        "@mlflow tags set" \
        "@mlflow test" \
        "@mlflow transition" \
        \
        "@object" \
        "@object open" \
        \
        "@publish" \
        \
        "@select" \
        \
        "@storage" \
        "@storage clear" \
        "@storage download_file" \
        "@storage exists" \
        "@storage list" \
        "@storage rm" \
        "@storage status" \
        \
        "@upload" \
        \
        "blue_objects"; do
        abcli_eval ,$options \
            abcli_help $module
        [[ $? -ne 0 ]] && return 1

        abcli_hr
    done

    return 0
}
