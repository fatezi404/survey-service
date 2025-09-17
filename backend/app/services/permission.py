from typing import Any

from app.models.user_model import User


async def has_permission(user: User, resource: str, action: str, context: dict[str, Any] | None = None) -> bool:
    context = context or {}

    def evaluate_conditions(conditions: dict[str, Any] | None = None, context: dict[str, Any] | None = None) -> bool:
        if not conditions:
            return True

        for condition_key, condition_value in conditions.items():
            if condition_key == 'self' and condition_value:
                if context.get('user_id') != context.get('target_user_id'):
                    return False

            if condition_key == 'creator' and condition_value:
                if context.get('user_id') != context.get('creator_id'):
                    return False

        return True

    for permission in user.direct_permissions:
        if (
            permission.resource == resource
            and permission.action == action
            and evaluate_conditions(permission.conditions, context)
        ):
            return True

    for role in user.roles:
        for permission in role.permissions:
            if (
                (permission.resource == resource or permission.resource == '*')
                and (permission.action == action or permission.action == '*')
                and evaluate_conditions(permission.conditions, context)
            ):
                return True

    return False
