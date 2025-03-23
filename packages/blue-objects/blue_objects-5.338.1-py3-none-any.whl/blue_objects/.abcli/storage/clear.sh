#! /usr/bin/env bash

function abcli_storage_clear() {
    local options=$1
    local do_dryrun=$(abcli_option_int "$options" dryrun 1)

    if [[ "$abcli_is_rpi" == true ]]; then
        abcli_eval dryrun=$do_dryrun \
            rm -rfv $ABCLI_OBJECT_ROOT
        return
    fi

    local recent_filename=$ABCLI_OBJECT_ROOT/QGIS-recent.yaml
    if [[ ! -f "$recent_filename" ]]; then
        abcli_log_warning "run \"QGIS.list_recent_projects\" first."
        return 1
    fi

    local recent_projects=$(python3 -c "from blue_objects import file; print('+'.join(file.load_yaml('$recent_filename')[1]))")
    abcli_log_list "$recent_projects" \
        --delim + \
        --after "object(s) to keep."

    pushd $ABCLI_OBJECT_ROOT >/dev/null
    local folder
    local object_name
    for folder in ./*; do
        object_name=$(basename "$folder")

        if [[ "+$recent_projects+" == *"+$object_name+"* ]]; then
            abcli_log "will keep $object_name ..."
        else
            abcli_log_warning "will delete $object_name ..."

            [[ "$do_dryrun" == 0 ]] &&
                rm -rfv $object_name
        fi
    done
    popd >/dev/null

    [[ "$do_dryrun" == 0 ]] &&
        rm -v $recent_filename

    return 0
}
