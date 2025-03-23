#! /usr/bin/env bash

function test_blue_objects_clone() {
    local options=$1

    local source_object_name=$(abcli_mlflow_tags_search \
        contains=latest-giza \
        --log 0 \
        --count 1)
    abcli_assert $source_object_name - non-empty

    local from_s3
    for from_s3 in 0 1; do
        local object_name=test_blue_objects_clone-$(abcli_string_timestamp_short)

        if [[ "$from_s3" == 0 ]]; then
            abcli_clone \
                ~relate,~tags,~upload,$options \
                $source_object_name \
                $object_name
            [[ $? -ne 0 ]] && return 1
        else
            abcli_clone \
                ~relate,s3,~upload,$options \
                $ABCLI_S3_OBJECT_PREFIX/$source_object_name \
                $object_name
            [[ $? -ne 0 ]] && return 1
        fi
    done

    return 0
}
