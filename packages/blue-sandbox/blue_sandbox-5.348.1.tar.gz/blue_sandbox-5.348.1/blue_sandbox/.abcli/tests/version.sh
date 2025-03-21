#! /usr/bin/env bash

function test_blue_sandbox_version() {
    local options=$1

    abcli_eval ,$options \
        "blue_sandbox version ${@:2}"
}
