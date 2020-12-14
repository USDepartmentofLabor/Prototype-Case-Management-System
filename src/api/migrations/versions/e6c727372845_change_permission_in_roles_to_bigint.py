"""change permission in roles to bigint

Revision ID: e6c727372845
Revises: 33aa8f9a620c
Create Date: 2019-12-24 19:03:22.333178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6c727372845'
down_revision = '33aa8f9a620c'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('roles', 'permissions', existing_type=sa.Integer(), type_=sa.BigInteger())


def downgrade():
    op.alter_column('roles', 'permissions', existing_type=sa.BigInteger(), type_=sa.Integer())
