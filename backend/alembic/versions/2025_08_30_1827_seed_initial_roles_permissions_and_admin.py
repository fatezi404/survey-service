"""seed initial roles permissions and admin

Revision ID: 169a44b639b4
Revises: bf4998cc7722
Create Date: 2025-08-30 18:27:22.249353

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '169a44b639b4'
down_revision: Union[str, None] = 'bf4998cc7722'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    roles_table = table(
        'roles',
        column('id', sa.Integer),
        column('name', sa.String)
    )

    permissions_table = table(
        'permissions',
        column('id', sa.Integer),
        column('name', sa.String),
        column('resource', sa.String),
        column('action', sa.String)
    )

    role_permissions_table = table(
        'role_permissions',
        column('role_id', sa.Integer),
        column('permission_id', sa.Integer)
    )

    users_table = table(
        'users',
        column('id', sa.Integer),
        column('username', sa.String),
        column('email', sa.String),
        column('hashed_password', sa.String),
        column('is_active', sa.Boolean),
        column('account_verified', sa.Boolean)
    )

    user_roles_table = table(
        'user_roles',
        column('user_id', sa.Integer),
        column('role_id', sa.Integer)
    )

    op.bulk_insert(roles_table, [
        {'id': 1, 'name': 'Admin'}
    ])

    op.bulk_insert(permissions_table, [
        {'id': 1, 'name': 'admin_all', 'resource': '*', 'action': '*'}
    ])

    op.bulk_insert(role_permissions_table, [
        {'role_id': 1, 'permission_id': 1}
    ])

    op.bulk_insert(users_table, [
        {'id': 1, 'username': 'Admin', 'email': 'admin@local.com',
         'hashed_password': '$2b$12$XtkK6d5pEREdbWsnkw8diOGnEcDLrp1C1x/Ikuh3MeF2cjeUWwLMO', # Admin1234
         'is_active': True, 'account_verified': True
         }
    ])

    op.bulk_insert(user_roles_table, [
        {'user_id': 1, 'role_id': 1}
    ])

def downgrade() -> None:
    op.execute('DELETE FROM user_roles WHERE user_id = 1 AND role_id = 1')
    op.execute('DELETE FROM users WHERE id = 1')
    op.execute('DELETE FROM role_permissions WHERE role_id = 1')
    op.execute('DELETE FROM permissions WHERE id = 1')
    op.execute('DELETE FROM roles WHERE id = 1')
