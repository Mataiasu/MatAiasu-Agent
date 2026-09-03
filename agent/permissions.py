from enum import StrEnum


class Permission(StrEnum):
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    RUN_COMMANDS = "run_commands"
    GIT = "git"
    NETWORK = "network"


class PermissionManager:
    def __init__(self, granted: set[Permission] | None = None) -> None:
        self.granted = granted or {Permission.READ_FILES}

    def allows(self, permission: Permission) -> bool:
        return permission in self.granted

    def require(self, permission: Permission) -> None:
        if not self.allows(permission):
            raise PermissionError(f"Permission required: {permission.value}")
