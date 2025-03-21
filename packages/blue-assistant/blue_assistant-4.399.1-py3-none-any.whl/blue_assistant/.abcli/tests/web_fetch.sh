#! /usr/bin/env bash

function test_blue_assistant_web_fetch() {
    local options=$1

    local object_name=test_blue_assistant_web_fetch-$(abcli_string_timestamp_short)

    abcli_eval ,$options \
        blue_assistant_web_fetch \
        ~upload \
        https://ode.rsl.wustl.edu/ \
        $object_name
}
