#! /usr/bin/env bash

function test_blue_assistant_script_list() {
    abcli_assert "$(blue_assistant_script_list \
        --delim + \
        --log 0)" \
        - non-empty
}
