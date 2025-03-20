# sparkplug
from sparkplug_core.permissions import (
    ActionPermission,
    IsNotAllowed,
    IsUser,
)


class FeatureFlag(
    ActionPermission,
):
    # user permissions
    create_perms = IsNotAllowed

    # object permissions
    read_perms = IsUser
    write_perms = IsNotAllowed
