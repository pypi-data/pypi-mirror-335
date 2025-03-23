#! /usr/bin/env bash

function blue_assistant_hue_create_user() {
    local options=$1
    local do_dryrun=$(abcli_option_int "$options" dryrun 0)

    abcli_eval dryrun=$do_dryrun \
        python3 -m blue_assistant.script.repository.hue \
        create_user \
        "${@:2}"
}
