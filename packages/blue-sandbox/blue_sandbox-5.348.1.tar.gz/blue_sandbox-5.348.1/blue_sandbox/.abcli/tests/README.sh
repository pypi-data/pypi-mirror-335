#! /usr/bin/env bash

function test_blue_sandbox_README() {
    local options=$1

    abcli_eval ,$options \
        blue_sandbox build_README
}
