import asyncio
import logging
import typing

import fastapi

from any_auth.backend import BackendClient
from any_auth.types.api_key import APIKey
from any_auth.types.role import NA_ROLE, Role, RoleUpdate
from any_auth.types.role_assignment import RoleAssignmentCreate
from any_auth.types.user import UserInDB

logger = logging.getLogger(__name__)


async def raise_if_role_assignment_denied(
    role_assignment_create: RoleAssignmentCreate,
    active_user_roles: typing.Tuple[UserInDB, typing.List[Role]],
    *,
    backend_client: BackendClient,
) -> typing.Literal[True]:
    """
    Validates role assignment permissions by checking role/user existence, NA role security rules, and ensuring the active user has permission to assign the requested role.
    """  # noqa: E501

    target_role = await raise_if_role_not_found(
        role_assignment_create, active_user_roles, backend_client=backend_client
    )
    target_subject = await raise_if_user_or_api_key_not_found(
        role_assignment_create, active_user_roles, backend_client=backend_client
    )

    if await allow_na_role(
        role_assignment_create,
        active_user_roles,
        backend_client=backend_client,
        target_subject=target_subject,
        target_role=target_role,
    ):
        logger.info(
            "Passed NA role check for target subject "
            + f"({target_subject.model_dump_json()}) "
            + f"with query body: ({role_assignment_create.model_dump_json()})"
        )
        return True

    await raise_if_assigning_role_not_in_user_child_roles(
        role_assignment_create, active_user_roles, backend_client=backend_client
    )

    return True


async def raise_if_role_not_found(
    role_assignment_create: RoleAssignmentCreate,
    active_user_roles: typing.Tuple[UserInDB, typing.List[Role]],
    *,
    backend_client: BackendClient,
) -> Role:
    role = await asyncio.to_thread(
        backend_client.roles.retrieve, id=role_assignment_create.role_id
    )
    if role is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return role


async def raise_if_user_or_api_key_not_found(
    role_assignment_create: RoleAssignmentCreate,
    active_user_roles: typing.Tuple[UserInDB, typing.List[Role]],
    *,
    backend_client: BackendClient,
) -> UserInDB | APIKey:
    if role_assignment_create.target_id.startswith("usr_"):
        user = await asyncio.to_thread(
            backend_client.users.retrieve, id=role_assignment_create.target_id
        )
        if user is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        else:
            return user

    # Try get user by id
    user = await asyncio.to_thread(
        backend_client.users.retrieve, id=role_assignment_create.target_id
    )

    # Try get api key by id if user is not found
    if user is None:
        api_key = await asyncio.to_thread(
            backend_client.api_keys.retrieve, role_assignment_create.target_id
        )
        if api_key is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail="Target ID of role assignment not found",
            )
        else:
            return api_key

    return user


async def allow_na_role(
    role_assignment_create: RoleAssignmentCreate,
    active_user_roles: typing.Tuple[UserInDB, typing.List[Role]],
    *,
    backend_client: BackendClient,
    target_subject: UserInDB | APIKey,
    target_role: Role | None = None,
) -> bool:
    if target_role is None:
        target_role = await asyncio.to_thread(
            backend_client.roles.retrieve, role_assignment_create.role_id
        )

    if target_role is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    role_na = await asyncio.to_thread(
        backend_client.roles.retrieve_by_id_or_name, NA_ROLE.name
    )
    if role_na is None:
        logger.warning(
            f"Role {NA_ROLE.name} not found, but user is trying to assign it"
        )
        return False

    if target_role.name != NA_ROLE.name:
        return False  # Not the NA role

    if (
        target_role.name == NA_ROLE.name
        and role_assignment_create.role_id == role_na.id
    ):
        if len(target_role.permissions) == 0:
            logger.info(
                f"Active user ({active_user_roles[0].model_dump_json()}) "
                + f"is trying to assign NA role ({role_na.model_dump_json()}) "
                + f"to subject ({target_subject.model_dump_json()}) "
                + f"with query body: ({role_assignment_create.model_dump_json()})"
            )
            return True
        else:
            logger.error(
                f"Denied NA role assignment for subject ({target_subject.model_dump_json()}) "  # noqa: E501
                + f"with query body: ({role_assignment_create.model_dump_json()}). "
                + "NA role should not have any permissions: "
                + f"{target_role.model_dump_json()}. "
            )
            logger.error(
                "NA role with permissions will cause a security risk. Hard code to "
                + "delete the permissions from the NA role in background."
            )
            await asyncio.to_thread(
                backend_client.roles.update,
                id=role_na.id,
                role_update=RoleUpdate(permissions=[]),
            )
            return False

    return False  # Not the NA role


async def raise_if_assigning_role_not_in_user_child_roles(
    role_assignment_create: RoleAssignmentCreate,
    active_user_roles: typing.Tuple[UserInDB, typing.List[Role]],
    *,
    backend_client: BackendClient,
) -> typing.Literal[True]:
    roles_map: typing.Dict[typing.Text, Role] = {
        role.id: role for role in active_user_roles[1]
    }

    # Get all child roles for the user
    for role in tuple(roles_map.values()):
        _all_child_roles = await asyncio.to_thread(
            backend_client.roles.retrieve_all_child_roles, role.id
        )
        roles_map.update({role.id: role for role in _all_child_roles})

    # Check if the role is in the user's child roles
    if role_assignment_create.role_id not in roles_map:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="Role not found in user's child roles",
        )

    return True
