#! /usr/bin/env bash

function blue_assistant_hue() {
    local task=$(abcli_unpack_keyword $1 help)

    local function_name=blue_assistant_hue_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    python3 -m blue_assistant.script.repository.hue "$@"
}

abcli_source_caller_suffix_path /hue
