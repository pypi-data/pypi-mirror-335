#! /usr/bin/env bash

function blue_sandbox() {
    local task=$(abcli_unpack_keyword $1 version)

    abcli_generic_task \
        plugin=blue_sandbox,task=$task \
        "${@:2}"
}

abcli_log $(blue_sandbox version --show_icon 1)
