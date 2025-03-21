#! /usr/bin/env bash

function blue_sandbox_browse() {
    local options=$1
    local what=$(abcli_option_choice "$options" actions,repo repo)

    local url="https://github.com/kamangir/blue-sandbox"
    [[ "$what" == "actions" ]] &&
        url="$url/actions"

    abcli_browse $url
}
