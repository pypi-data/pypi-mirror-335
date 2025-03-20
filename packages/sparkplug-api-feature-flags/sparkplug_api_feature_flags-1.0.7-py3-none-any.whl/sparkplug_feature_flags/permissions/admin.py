# sparkplug
from sparkplug_core.permissions import (
    ActionPermission,
    IsAdmin,
    IsNotAllowed,
)


class Admin(
    ActionPermission,
):
    # user permissions
    create_perms = IsNotAllowed

    # object permissions
    read_perms = IsAdmin
    write_perms = IsAdmin
