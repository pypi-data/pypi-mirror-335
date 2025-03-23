#! /usr/bin/env bash

function test_blue_assistant_version() {
    local options=$1

    abcli_eval ,$options \
        "blue_assistant version ${@:2}"
}
