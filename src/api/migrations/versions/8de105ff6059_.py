"""empty message

Revision ID: 8de105ff6059
Revises: db3e7aca78f6
Create Date: 2020-03-24 20:29:57.940737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8de105ff6059'
down_revision = 'db3e7aca78f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('roles', 'default',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('roles', 'name',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    op.alter_column('roles', 'permissions',
               existing_type=sa.BIGINT(),
               nullable=False)
    op.add_column('surveys', sa.Column('reporting_table_name', sa.String(length=128), nullable=True))
    op.drop_column('surveys', 'mongo_collection_name')
    op.add_column('surveys_version', sa.Column('reporting_table_name', sa.String(length=128), autoincrement=False, nullable=True))
    op.drop_column('surveys_version', 'mongo_collection_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('surveys_version', sa.Column('mongo_collection_name', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.drop_column('surveys_version', 'reporting_table_name')
    op.add_column('surveys', sa.Column('mongo_collection_name', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.drop_column('surveys', 'reporting_table_name')
    op.alter_column('roles', 'permissions',
               existing_type=sa.BIGINT(),
               nullable=True)
    op.alter_column('roles', 'name',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    op.alter_column('roles', 'default',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
