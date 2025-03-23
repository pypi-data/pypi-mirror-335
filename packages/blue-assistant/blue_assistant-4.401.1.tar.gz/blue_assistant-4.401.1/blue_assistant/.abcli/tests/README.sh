#! /usr/bin/env bash

function test_blue_assistant_README() {
    local options=$1

    abcli_eval ,$options \
        blue_assistant build_README
}



