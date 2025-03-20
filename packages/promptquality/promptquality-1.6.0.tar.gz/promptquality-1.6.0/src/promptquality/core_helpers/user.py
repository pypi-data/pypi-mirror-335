from typing import Optional

from pydantic import UUID4

from galileo_core.helpers.user import get_current_user as core_get_current_user
from galileo_core.helpers.user import invite_users as core_invite_users
from galileo_core.helpers.user import list_users as core_list_users
from galileo_core.schemas.core.auth_method import AuthMethod
from galileo_core.schemas.core.user import User
from galileo_core.schemas.core.user_role import UserRole
from promptquality.types.config import PromptQualityConfig


def get_current_user() -> User:
    config = PromptQualityConfig.get()
    return core_get_current_user(config=config)


def invite_users(
    emails: list[str],
    role: UserRole = UserRole.user,
    group_ids: Optional[list[UUID4]] = None,
    auth_method: AuthMethod = AuthMethod.email,
) -> None:
    config = PromptQualityConfig.get()
    return core_invite_users(emails=emails, role=role, group_ids=group_ids, auth_method=auth_method, config=config)


def list_users() -> list[User]:
    config = PromptQualityConfig.get()
    return core_list_users(config=config)
