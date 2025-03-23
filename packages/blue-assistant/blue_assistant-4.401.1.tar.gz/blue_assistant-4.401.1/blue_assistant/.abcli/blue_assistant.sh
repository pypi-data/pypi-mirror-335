#! /usr/bin/env bash

function blue_assistant() {
    local task=$(abcli_unpack_keyword $1 version)

    abcli_generic_task \
        plugin=blue_assistant,task=$task \
        "${@:2}"
}

abcli_log $(blue_assistant version --show_icon 1)
