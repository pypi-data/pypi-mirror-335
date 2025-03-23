#! /usr/bin/env bash

function blue_assistant_script_list() {
    python3 -m blue_assistant.script \
        list \
        "$@"
}
