#! /usr/bin/env bash

function blue_assistant_web_crawl() {
    local options=$1
    local do_dryrun=$(abcli_option_int "$options" dryrun 0)
    local do_download=$(abcli_option_int "$options" download $(abcli_not $do_dryrun))
    local do_upload=$(abcli_option_int "$options" upload $(abcli_not $do_dryrun))

    local seed_urls=${2:-void}

    local object_name=$(abcli_clarify_object $3 web-crawl-$(abcli_string_timestamp_short))
    [[ "$do_download" == 1 ]] &&
        abcli_download - $object_name

    abcli_log "crawling $seed_urls -> $object_name ..."

    abcli_eval dryrun=$do_dryrun \
        python3 -m blue_assistant.web \
        crawl \
        --seed_urls $seed_urls \
        --object_name $object_name \
        "${@:4}"
    [[ $? -ne 0 ]] && return 1

    [[ "$do_upload" == 1 ]] &&
        abcli_upload - $object_name

    return 0
}
