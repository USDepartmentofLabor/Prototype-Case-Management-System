"""change id in roles to bigint

Revision ID: 33aa8f9a620c
Revises: d6a646364c7b
Create Date: 2019-12-24 19:01:14.072797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33aa8f9a620c'
down_revision = 'd6a646364c7b'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('roles', 'id', existing_type=sa.Integer(), type_=sa.BigInteger())


def downgrade():
    op.alter_column('roles', 'id', existing_type=sa.BigInteger(), type_=sa.Integer())
