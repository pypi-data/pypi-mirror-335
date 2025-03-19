import datetime
from datetime import date
from random import choice
from string import ascii_letters, digits
from typing import Annotated, Any, Dict, List, Set

import pymongo
import regex
from beanie import Document, Indexed, Link, PydanticObjectId
from pydantic import model_validator
from pymongo import ASCENDING, IndexModel
from pytz import UTC

from fa_common.auth.models import AuthUser
from fa_common.config import get_settings
from fa_common.models import StorageLocation, TimeStampedModel
from fa_common.routes.modules.models import ModuleDocument
from fa_common.routes.user.enums import AccessLevel, PermissionType
from fa_common.routes.user.types import BaseRole, Permission, PermissionDef
from fa_common.utils import uuid4_as_str


class RoleDB(Document, BaseRole):
    # users: list[BackLink["UserDB"]] = Field(original_field="app_roles")  # Back links don't work very well as of 5/11/24
    """Back link to users with this role. Use primary for cleaning up user roles on delete"""

    @classmethod
    async def auto_assigned_roles(cls, email: str) -> list["RoleDB"]:
        roles = []
        auto_roles = await cls.find(cls.allow_auto_assign == True).to_list()  # noqa

        for role in auto_roles:
            if not role.auto_assign_email_regex or regex.match(role.auto_assign_email_regex, email) is not None:
                roles.append(role)
        return roles

    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}roles"
        indexes = [IndexModel([("name", ASCENDING)], name="role_name_index", unique=True)]


class AppDB(Document, TimeStampedModel):
    """
    TODO: Extend this model to provide fields required for the app gallery and module management
    """

    slug: Annotated[str, Indexed(unique=True)]
    """Unique identifier for the app used for scopes"""
    name: str
    description: str | None = None
    allowed_permissions: list[PermissionDef]
    """List of permission definitions that this app uses"""
    root_app: bool = False
    module: Link[ModuleDocument] | None = None

    @model_validator(mode="before")
    @classmethod
    def check_name(cls, data: Any) -> Any:
        if isinstance(data, dict) and "slug" not in data and "name" in data:
            data["slug"] = data["name"].lower().replace(" ", "_")
            # truncate to 20 characters or less
            data["slug"] = data["slug"][:20] if len(data["slug"]) > 20 else data["slug"]
        return data

    def get_access_scope(self, level: AccessLevel) -> str:
        for perm in self.allowed_permissions:
            if perm.type == PermissionType.APP_ACCESS:
                return f"{self.slug}_access_{level.name.lower()}"
        raise ValueError("No access permission found for this app")

    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}apps"


class UserDB(Document, TimeStampedModel, AuthUser):
    """User database model."""

    valid_user: bool = True
    settings: Dict[str, Any] | None = None
    """User settings, may be app specific."""
    storage: Dict[str, StorageLocation] = {}
    """Key is use to distinguish between different apps."""
    api_key: str | None = None

    app_roles: list[Link[RoleDB]] | None = None
    permissions: List[Permission] = []

    @staticmethod
    def _api_out_exclude() -> Set[str]:
        """Fields to exclude from an API output."""
        return {"updated_at", "created", "valid_user"}

    async def set_roles(self, roles: List[str]):
        for role in roles:
            self.roles.append(role)

        await self.save()  # type: ignore

    async def generate_api_key(self):
        new_key = uuid4_as_str()

        duplicates = await self.find(UserDB.api_key == new_key).to_list()
        if duplicates is not None and len(duplicates) > 0:
            raise ValueError("Generating API key encountered a duplicate, please try again.")
        self.api_key = new_key
        await self.save()  # type: ignore
        return self.api_key

    async def apply_permissions(self, permissions: List[Permission], save: bool = True):
        """
        if items in permissions have a name that is unique within self.permissions then add it to the list, if the name is a duplicate keep
        the permission with the latest expiry or the highest value
        """
        for perm in permissions:
            found = False
            replaced = False
            top_value = -2
            top_expiry: date | None = datetime.datetime.now(tz=UTC).date()
            for i, existing_perm in enumerate(self.permissions):
                if existing_perm.name == perm.name:
                    found = True
                    if (
                        (existing_perm.expiry is not None and (perm.expiry is None or perm.expiry > existing_perm.expiry))
                        or existing_perm.expiry == perm.expiry
                        and perm.get_value() >= existing_perm.get_value()
                    ):
                        # If new permission has better or the same expiry and better or same value
                        replaced = True
                        self.permissions[i] = perm
                        break
                    top_value = max(top_value, existing_perm.get_value())
                    top_expiry = None if (top_expiry or existing_perm.expiry is None) else max(top_expiry, existing_perm.expiry)

            if not found or (not replaced and (perm.expiry == top_expiry or perm.get_value() == top_value)):
                # Not found or has something that is better
                self.permissions.append(perm)

        await self.refresh_permissions(save)

    async def remove_permissions_by_ref(self, reference: str, save: bool = True):
        """Remove permissions that were applied by a specific reference"""
        self.permissions = [perm for perm in self.permissions if perm.applied_by != reference]
        await self.refresh_permissions(save)

    async def refresh_permissions(self, save: bool = True):
        for perm in self.permissions:
            if perm.is_expired():
                self.permissions.remove(perm)

        await self.update_scopes(save=save)

    async def update_scopes(self, save: bool = True):
        """Update the scopes based on the roles and app roles. Scopes are used for API permissions"""
        scopes = set()

        if self.permissions is not None:
            for perm in self.permissions:
                scopes.update(perm.as_scopes())

        if self.app_roles is not None:
            for role in self.app_roles:
                if isinstance(role, RoleDB):
                    for perm in role.permissions:  # type: ignore
                        scopes.update(perm.as_scopes())

        self.scopes = list(scopes)
        if save:
            await self.save()

    def add_custom_storage_location(self, location_id: str, location: StorageLocation):
        self.storage[location_id] = location

    def create_user_storage_location(self, location_id: str):
        if self.id is None:
            raise ValueError("Trying to set a user folder on a user without an ID")

        if location_id in self.storage:
            raise ValueError(f"Storage location {location_id} already exists")

        self.storage[location_id] = StorageLocation(
            app_created=True, bucket_name=get_settings().BUCKET_NAME, path_prefix=self.generate_storage_path(self.name, self.sub)
        )

    def get_storage_location(self, location_id: str, create=True) -> StorageLocation:
        if location_id not in self.storage:
            if create:
                self.create_user_storage_location(location_id)
            else:
                raise ValueError(f"Storage location {location_id} does not exist")

        return self.storage[location_id]

    @classmethod
    def generate_user_prefix(cls, name: str) -> str:
        if len(name) >= 3:
            return name[:3].lower()
        elif name != "":
            return name.lower()
        else:
            return "".join(choice(ascii_letters + digits) for _ in range(3))

    @classmethod
    def generate_storage_path(cls, name: str, user_id: str | PydanticObjectId) -> str:
        # # S3 + GCP bucket naming standard (S3 is more strict), all lowercase and no '_'
        # # Adding prefix to avoid potential conflicts from going all lowercase

        np = cls.generate_user_prefix(name)
        return f"{get_settings().BUCKET_USER_FOLDER}{np}-{str(user_id).lower()}"

    class Settings:
        name = f"{get_settings().COLLECTION_PREFIX}user"
        indexes = [pymongo.IndexModel([("sub", pymongo.ASCENDING)], unique=True)]
