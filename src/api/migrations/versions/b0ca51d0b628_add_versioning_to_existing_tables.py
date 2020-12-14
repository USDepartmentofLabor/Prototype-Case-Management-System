"""add versioning to existing tables

Revision ID: b0ca51d0b628
Revises: 096b6f6fa1c4
Create Date: 2019-12-18 06:44:14.626519

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b0ca51d0b628'
down_revision = '096b6f6fa1c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('case_definitions_surveys_version',
    sa.Column('case_definition_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('survey_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('transaction_id')
    )
    op.create_index(op.f('ix_case_definitions_surveys_version_end_transaction_id'), 'case_definitions_surveys_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_case_definitions_surveys_version_operation_type'), 'case_definitions_surveys_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_case_definitions_surveys_version_transaction_id'), 'case_definitions_surveys_version', ['transaction_id'], unique=False)
    op.create_table('case_definitions_version',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(), autoincrement=False, nullable=True),
    sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('created_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('created_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('updated_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_case_definitions_version_created_at'), 'case_definitions_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_case_definitions_version_end_transaction_id'), 'case_definitions_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_case_definitions_version_operation_type'), 'case_definitions_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_case_definitions_version_transaction_id'), 'case_definitions_version', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_case_definitions_version_updated_at'), 'case_definitions_version', ['updated_at'], unique=False)
    op.create_table('roles_version',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=64), autoincrement=False, nullable=True),
    sa.Column('default', sa.Boolean(), autoincrement=False, nullable=True),
    sa.Column('permissions', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_roles_version_default'), 'roles_version', ['default'], unique=False)
    op.create_index(op.f('ix_roles_version_end_transaction_id'), 'roles_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_roles_version_operation_type'), 'roles_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_roles_version_transaction_id'), 'roles_version', ['transaction_id'], unique=False)
    op.create_table('surveys_version',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(), autoincrement=False, nullable=True),
    sa.Column('structure', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('is_archived', sa.Boolean(), autoincrement=False, nullable=True),
    sa.Column('mongo_collection_name', sa.String(length=128), autoincrement=False, nullable=True),
    sa.Column('created_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('created_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('updated_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_surveys_version_created_at'), 'surveys_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_surveys_version_end_transaction_id'), 'surveys_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_surveys_version_name'), 'surveys_version', ['name'], unique=False)
    op.create_index(op.f('ix_surveys_version_operation_type'), 'surveys_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_surveys_version_transaction_id'), 'surveys_version', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_surveys_version_updated_at'), 'surveys_version', ['updated_at'], unique=False)
    op.create_table('users_version',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('email', sa.String(length=64), autoincrement=False, nullable=True),
    sa.Column('username', sa.String(length=64), autoincrement=False, nullable=True),
    sa.Column('role_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('password_hash', sa.String(length=128), autoincrement=False, nullable=True),
    sa.Column('name', sa.String(length=64), autoincrement=False, nullable=True),
    sa.Column('location', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('last_seen_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('is_active', sa.Boolean(), autoincrement=False, nullable=True),
    sa.Column('created_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_users_version_created_at'), 'users_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_version_email'), 'users_version', ['email'], unique=False)
    op.create_index(op.f('ix_users_version_end_transaction_id'), 'users_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_users_version_operation_type'), 'users_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_users_version_transaction_id'), 'users_version', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_users_version_updated_at'), 'users_version', ['updated_at'], unique=False)
    op.create_index(op.f('ix_users_version_username'), 'users_version', ['username'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_version_username'), table_name='users_version')
    op.drop_index(op.f('ix_users_version_updated_at'), table_name='users_version')
    op.drop_index(op.f('ix_users_version_transaction_id'), table_name='users_version')
    op.drop_index(op.f('ix_users_version_operation_type'), table_name='users_version')
    op.drop_index(op.f('ix_users_version_end_transaction_id'), table_name='users_version')
    op.drop_index(op.f('ix_users_version_email'), table_name='users_version')
    op.drop_index(op.f('ix_users_version_created_at'), table_name='users_version')
    op.drop_table('users_version')
    op.drop_index(op.f('ix_surveys_version_updated_at'), table_name='surveys_version')
    op.drop_index(op.f('ix_surveys_version_transaction_id'), table_name='surveys_version')
    op.drop_index(op.f('ix_surveys_version_operation_type'), table_name='surveys_version')
    op.drop_index(op.f('ix_surveys_version_name'), table_name='surveys_version')
    op.drop_index(op.f('ix_surveys_version_end_transaction_id'), table_name='surveys_version')
    op.drop_index(op.f('ix_surveys_version_created_at'), table_name='surveys_version')
    op.drop_table('surveys_version')
    op.drop_index(op.f('ix_roles_version_transaction_id'), table_name='roles_version')
    op.drop_index(op.f('ix_roles_version_operation_type'), table_name='roles_version')
    op.drop_index(op.f('ix_roles_version_end_transaction_id'), table_name='roles_version')
    op.drop_index(op.f('ix_roles_version_default'), table_name='roles_version')
    op.drop_table('roles_version')
    op.drop_index(op.f('ix_case_definitions_version_updated_at'), table_name='case_definitions_version')
    op.drop_index(op.f('ix_case_definitions_version_transaction_id'), table_name='case_definitions_version')
    op.drop_index(op.f('ix_case_definitions_version_operation_type'), table_name='case_definitions_version')
    op.drop_index(op.f('ix_case_definitions_version_end_transaction_id'), table_name='case_definitions_version')
    op.drop_index(op.f('ix_case_definitions_version_created_at'), table_name='case_definitions_version')
    op.drop_table('case_definitions_version')
    op.drop_index(op.f('ix_case_definitions_surveys_version_transaction_id'), table_name='case_definitions_surveys_version')
    op.drop_index(op.f('ix_case_definitions_surveys_version_operation_type'), table_name='case_definitions_surveys_version')
    op.drop_index(op.f('ix_case_definitions_surveys_version_end_transaction_id'), table_name='case_definitions_surveys_version')
    op.drop_table('case_definitions_surveys_version')
    # ### end Alembic commands ###