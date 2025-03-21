#! /usr/bin/env bash

function test_blue_sandbox_help() {
    local options=$1

    local module
    for module in \
        "@sandbox" \
        \
        "blue_sandbox"; do
        abcli_eval ,$options \
            abcli_help $module
        [[ $? -ne 0 ]] && return 1

        abcli_hr
    done

    return 0
}
