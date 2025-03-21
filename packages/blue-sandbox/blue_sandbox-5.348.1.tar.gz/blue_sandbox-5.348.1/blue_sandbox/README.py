import os

from blue_objects import file, README

from blue_sandbox import NAME, VERSION, ICON, REPO_NAME


items = README.Items(
    [
        {
            "name": "virtualcam",
            "url": "./blue_sandbox/virtualcam",
            "marquee": "https://github.com/kamangir/assets/raw/main/blue-sandbox/virtualcam.png?raw=true",
            "description": "Python + [OBS Studio](https://obsproject.com/) ⏸️",
        },
        {},
        {},
    ]
)


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            cols=3,
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
        )
        for readme in [
            {
                "path": "..",
                "items": items,
            },
            {"path": "./virtualcam"},
        ]
    )
