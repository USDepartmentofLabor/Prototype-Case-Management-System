"""add projects

Revision ID: 373907e5c797
Revises: 7a2eb67deda8
Create Date: 2020-02-24 23:08:21.845310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '373907e5c797'
down_revision = '7a2eb67deda8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('projects_version',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=64), autoincrement=False, nullable=True),
    sa.Column('title', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('organization', sa.String(length=64), autoincrement=False, nullable=True),
    sa.Column('agreement_number', sa.String(length=30), autoincrement=False, nullable=True),
    sa.Column('start_date', sa.Date(), autoincrement=False, nullable=True),
    sa.Column('end_date', sa.Date(), autoincrement=False, nullable=True),
    sa.Column('funding_amount', sa.Float(), autoincrement=False, nullable=True),
    sa.Column('location', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('created_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('created_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('updated_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_projects_version_created_at'), 'projects_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_projects_version_end_transaction_id'), 'projects_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_projects_version_name'), 'projects_version', ['name'], unique=False)
    op.create_index(op.f('ix_projects_version_operation_type'), 'projects_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_projects_version_transaction_id'), 'projects_version', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_projects_version_updated_at'), 'projects_version', ['updated_at'], unique=False)
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('organization', sa.String(length=64), nullable=True),
    sa.Column('agreement_number', sa.String(length=30), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('funding_amount', sa.Float(), nullable=True),
    sa.Column('location', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=False),
    sa.Column('updated_by_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_created_at'), 'projects', ['created_at'], unique=False)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=True)
    op.create_index(op.f('ix_projects_updated_at'), 'projects', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_projects_updated_at'), table_name='projects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_created_at'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_projects_version_updated_at'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_transaction_id'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_operation_type'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_name'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_end_transaction_id'), table_name='projects_version')
    op.drop_index(op.f('ix_projects_version_created_at'), table_name='projects_version')
    op.drop_table('projects_version')
    # ### end Alembic commands ###