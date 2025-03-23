#! /usr/bin/env bash

function test_blue_assistant_RAG_query_pdf() {
    local options=$1

    local object_name=$(abcli_mlflow_tags_search \
        contains=latest-giza \
        --log 0 \
        --count 1)
    abcli_assert $object_name - non-empty

    blue_assistant_RAG_query_pdf \
        ~upload,filename=giza,$options \
        $object_name \
        "What is the importance of Bash in AI? in less than 20 words."
}
