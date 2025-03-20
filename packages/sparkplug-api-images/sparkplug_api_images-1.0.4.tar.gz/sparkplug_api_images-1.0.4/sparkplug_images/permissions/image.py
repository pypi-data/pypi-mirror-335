# project
from sparkplug_core.permissions import (
    ActionPermission,
    IsCreator,
    IsAuthenticated,
)


class Image(
    ActionPermission,
):
    # user permissions
    create_perms = IsAuthenticated

    # object permissions
    read_perms = IsAuthenticated
    write_perms = IsCreator
