import datetime
from datetime import date

from pydantic import AnyUrl, Field, computed_field
from pytz import UTC

from fa_common.models import CamelModel
from fa_common.routes.user.enums import AccessLevel, PermissionType


class PermissionDef(CamelModel):
    type: PermissionType = PermissionType.APP_ACCESS
    feature_name: str | None = None
    """Name of the app feature, required for APP_FEATURE permission"""
    app_slug: str
    """The app this permission is associated with, this should exactly match the AppDB slug."""

    @computed_field
    @property
    def name(self) -> str:
        if self.type == PermissionType.APP_ACCESS:
            return f"{self.app_slug}_access"
        elif self.type == PermissionType.APP_FEATURE:
            if not self.feature_name:
                raise ValueError("Feature name must be provided for APP_FEATURE permission")
            return f"{self.app_slug}_{self.feature_name}"
        raise ValueError("Permission type not recognised")

    @staticmethod
    def access_scope_name(app_slug: str, level: AccessLevel) -> str:
        if not level:
            raise ValueError("Level must be provided for APP_ACCESS permission")
        return f"{app_slug}_access_{level.name.lower()}"


class Permission(PermissionDef):
    """Applied permission"""

    expiry: date | None = None
    value: int | AccessLevel | None = None
    """Context sensitive field that could denote access level or some other restriction"""
    applied_by: str | None = None
    """The licence ID, User ID or other reference for what applied this permissions"""

    def get_value(self) -> int:
        """Used for comparions of which permission is better"""
        if self.value is None:
            return -1

        return self.value if isinstance(self.value, int) else self.value.value

    def as_scopes(self) -> list[str]:
        scopes = []

        if self.type == PermissionType.APP_ACCESS:
            # Create a scope for each access level at or below the current int value excluding 0
            if not self.value:
                raise ValueError("Value must be set for APP_ACCESS permission")
            for level in AccessLevel:
                self_value = self.value if isinstance(self.value, int) else self.value.value
                if level.value <= self_value and level.value > 0:
                    scopes.append(self.access_scope_name(self.app_slug, level))
        else:
            scopes.append(self.name)

        return scopes

    def is_expired(self) -> bool:
        return self.expiry is not None and self.expiry < datetime.datetime.now(tz=UTC).date()


class BaseRole(CamelModel):
    name: str = Field(..., max_length=20, description="Unique name for the role", pattern=r"^[a-z0-9_]+$")
    description: str | None = None
    permissions: list[Permission] = []

    allow_auto_assign: bool = False
    """If true this role will be automatically assigned either always or based on an email address"""
    auto_assign_email_regex: str | None = None
    """Regex to match email addresses that should automatically be assigned this role if None all emails will be considered a match"""


class UpdateUserMe(CamelModel):
    name: str | None = None
    picture: AnyUrl | None = None
    country: str | None = None
    nickname: str | None = None


class UpdateUser(UpdateUserMe):
    app_role_name: list[str] = []
    permissions: list[Permission] = []
