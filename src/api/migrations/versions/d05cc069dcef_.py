"""empty message

Revision ID: d05cc069dcef
Revises: 3a37fa7085e6
Create Date: 2019-11-13 19:33:53.740098

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd05cc069dcef'
down_revision = '3a37fa7085e6'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('users', 'location', existing_type=sa.String(64), type_=sa.Text())


def downgrade():
    op.alter_column('users', 'location', existing_type=sa.Text(), type_=sa.String(64))
