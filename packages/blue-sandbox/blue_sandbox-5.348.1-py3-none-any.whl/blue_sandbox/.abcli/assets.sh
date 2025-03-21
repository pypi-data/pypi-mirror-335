#! /usr/bin/env bash

function abcli_assets() {
    local task=$(abcli_unpack_keyword $1 help)

    local function_name=abcli_assets_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    python3 -m blue_sandbox.assets "$@"
}

abcli_source_caller_suffix_path /assets
