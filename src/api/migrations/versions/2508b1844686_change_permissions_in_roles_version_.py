"""change permissions in roles version table to bigint

Revision ID: 2508b1844686
Revises: e6c727372845
Create Date: 2019-12-25 08:57:05.214479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2508b1844686'
down_revision = 'e6c727372845'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('roles_version', 'permissions', existing_type=sa.Integer(), type_=sa.BigInteger())


def downgrade():
    op.alter_column('roles_version', 'permissions', existing_type=sa.BigInteger(), type_=sa.Integer())
