#! /usr/bin/env bash

function blue_assistant_web_fetch() {
    local options=$1
    local do_dryrun=$(abcli_option_int "$options" dryrun 0)
    local do_upload=$(abcli_option_int "$options" upload $(abcli_not $do_dryrun))

    local url=${2:-void}

    local object_name=$(abcli_clarify_object $3 web-fetch-$(abcli_string_timestamp_short))

    abcli_log "fetching $url -> $object_name ..."

    abcli_eval dryrun=$do_dryrun \
        python3 -m blue_assistant.web \
        fetch \
        --url $url \
        --object_name $object_name \
        "${@:4}"
    [[ $? -ne 0 ]] && return 1

    [[ "$do_upload" == 1 ]] &&
        abcli_upload - $object_name

    return 0
}
