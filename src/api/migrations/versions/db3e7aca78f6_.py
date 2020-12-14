"""empty message

Revision ID: db3e7aca78f6
Revises: 373907e5c797
Create Date: 2020-03-18 18:25:39.727394

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db3e7aca78f6'
down_revision = '373907e5c797'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('error_codes')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('error_codes',
    sa.Column('code', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('message', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('code', name='error_codes_pkey')
    )
    # ### end Alembic commands ###