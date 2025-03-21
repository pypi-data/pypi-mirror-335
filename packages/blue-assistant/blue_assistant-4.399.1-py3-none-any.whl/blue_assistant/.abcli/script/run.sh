#! /usr/bin/env bash

function blue_assistant_script_run() {
    local options=$1
    local do_dryrun=$(abcli_option_int "$options" dryrun 0)
    local do_download=$(abcli_option_int "$options" download $(abcli_not $do_dryrun))
    local do_upload=$(abcli_option_int "$options" upload $(abcli_not $do_dryrun))

    local script_options=$2
    local script_name=$(abcli_option "$script_options" script base)
    local script_version=$(abcli_option "$script_options" version base)

    local object_name=$(abcli_clarify_object $3 $script_name-$script_version-$(abcli_string_timestamp_short))
    [[ "$do_download" == 1 ]] &&
        abcli_download - $object_name

    abcli_log "running $script_name -> $object_name ..."

    abcli_eval dryrun=$do_dryrun \
        python3 -m blue_assistant.script \
        run \
        --script_name $script_name \
        --script_version $script_version \
        --object_name $object_name \
        "${@:4}"
    [[ $? -ne 0 ]] && return 1

    [[ "$do_upload" == 1 ]] &&
        abcli_upload - $object_name

    return 0
}
