import os

from blueness import module

from blue_objects import NAME as MY_NAME
from blue_objects import file
from blue_objects.README.functions import build
from blue_objects.README.items import Items
from blue_objects.logger import logger

MY_NAME = module.name(__file__, MY_NAME)


def build_me() -> bool:
    from blue_objects import NAME, VERSION, REPO_NAME, ICON

    return all(
        build(
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
        )
        for readme in [
            {"path": "../.."},
            {"path": "."},
        ]
    )
