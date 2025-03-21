from typing import List

from pydantic import UUID4, BaseModel, Field

from galileo_core.schemas.core.auth_method import AuthMethod
from galileo_core.schemas.core.user_role import UserRole


class InviteUsersRequest(BaseModel):
    auth_method: AuthMethod = AuthMethod.email
    emails: List[str] = Field(default_factory=list)
    role: UserRole = UserRole.user
    group_ids: List[UUID4] = []


class User(BaseModel):
    id: UUID4
    email: str
    role: UserRole = UserRole.user


class UpdateUserRoleRequest(BaseModel):
    role: UserRole
