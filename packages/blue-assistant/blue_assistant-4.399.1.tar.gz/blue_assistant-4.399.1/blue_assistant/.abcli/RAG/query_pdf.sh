#! /usr/bin/env bash

function blue_assistant_RAG_query_pdf() {
    local options=$1
    local do_dryrun=$(abcli_option_int "$options" dryrun 0)
    local do_download=$(abcli_option_int "$options" download $(abcli_not $do_dryrun))
    local filename=$(abcli_option "$options" filename document.pdf)
    local do_upload=$(abcli_option_int "$options" upload $(abcli_not $do_dryrun))

    local object_name=$(abcli_clarify_object $2 .)
    [[ "$do_download" == 1 ]] &&
        abcli_download - $object_name

    local question=${3:-void}
    local encoded_question=${question// /__}

    abcli_eval dryrun=$do_dryrun \
        python3 -m blue_assistant.RAG \
        query_pdf \
        --object_name $object_name \
        --filename $filename \
        --encoded_question $encoded_question \
        "${@:4}"
    [[ $? -ne 0 ]] && return 1

    [[ "$do_upload" == 1 ]] &&
        abcli_upload - $object_name

    return 0
}
