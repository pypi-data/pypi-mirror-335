#! /usr/bin/env bash

function abcli_assets_publish() {
    local options=$1

    local do_download=$(abcli_option_int "$options" download 0)
    local do_pull=$(abcli_option_int "$options" pull 1)
    local do_push=$(abcli_option_int "$options" push 0)
    local extensions=$(abcli_option "$options" extensions png+geojson)

    [[ "$do_pull" == 1 ]] &&
        abcli_git \
            assets \
            pull \
            ~all

    local object_name=$(abcli_clarify_object $2 .)

    [[ "$do_download" == 1 ]] &&
        abcli_download - $object_name

    abcli_eval dryrun=$do_dryrun \
        python3 -m blue_sandbox.assets \
        publish \
        --object_name $object_name \
        --extensions $extensions \
        "${@:3}"
    [[ $? -ne 0 ]] && return 1

    [[ "$do_push" == 1 ]] &&
        abcli_git \
            assets \
            push \
            "$object_name update."

    return 0
}
