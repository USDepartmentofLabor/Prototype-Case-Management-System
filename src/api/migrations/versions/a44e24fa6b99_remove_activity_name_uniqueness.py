"""remove activity name uniqueness

Revision ID: a44e24fa6b99
Revises: 049b4cbce413
Create Date: 2020-11-05 18:04:12.998699

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a44e24fa6b99'
down_revision = '049b4cbce413'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('activities_name_key', 'activities', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('activities_name_key', 'activities', ['name'])
    # ### end Alembic commands ###
