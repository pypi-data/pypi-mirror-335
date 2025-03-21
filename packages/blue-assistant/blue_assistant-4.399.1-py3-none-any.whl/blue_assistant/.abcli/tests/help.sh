#! /usr/bin/env bash

function test_blue_assistant_help() {
    local options=$1

    local module
    for module in \
        "@assistant" \
        \
        "@assistant pypi" \
        "@assistant pypi browse" \
        "@assistant pypi build" \
        "@assistant pypi install" \
        \
        "@assistant pytest" \
        \
        "@assistant test" \
        "@assistant test list" \
        \
        "@assistant browse" \
        \
        "@assistant script" \
        "@assistant script list" \
        "@assistant script run" \
        \
        "@hue" \
        "@hue create_user" \
        "@hue list" \
        "@hue set" \
        "@hue test" \
        \
        "@RAG" \
        "@RAG query_pdf" \
        \
        "@web" \
        "@web crawl" \
        "@web fetch" \
        \
        "blue_assistant"; do
        abcli_eval ,$options \
            abcli_help $module
        [[ $? -ne 0 ]] && return 1

        abcli_hr
    done

    return 0
}
