"""add cases

Revision ID: d6a646364c7b
Revises: 525d54d17131
Create Date: 2019-12-24 18:18:42.361362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6a646364c7b'
down_revision = '525d54d17131'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('case_notes_version',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('case_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('note', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('created_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('created_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('updated_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_case_notes_version_created_at'), 'case_notes_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_case_notes_version_end_transaction_id'), 'case_notes_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_case_notes_version_operation_type'), 'case_notes_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_case_notes_version_transaction_id'), 'case_notes_version', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_case_notes_version_updated_at'), 'case_notes_version', ['updated_at'], unique=False)
    op.create_table('cases_version',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('key', sa.String(), autoincrement=False, nullable=True),
    sa.Column('name', sa.String(), autoincrement=False, nullable=True),
    sa.Column('description', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('case_definition_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('created_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('created_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('updated_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_cases_version_created_at'), 'cases_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_cases_version_end_transaction_id'), 'cases_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_cases_version_operation_type'), 'cases_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_cases_version_transaction_id'), 'cases_version', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_cases_version_updated_at'), 'cases_version', ['updated_at'], unique=False)
    op.create_table('cases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('case_definition_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=False),
    sa.Column('updated_by_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['case_definition_id'], ['case_definitions.id'], ),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_cases_created_at'), 'cases', ['created_at'], unique=False)
    op.create_index(op.f('ix_cases_updated_at'), 'cases', ['updated_at'], unique=False)
    op.create_table('case_notes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('case_id', sa.Integer(), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=False),
    sa.Column('updated_by_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_case_notes_created_at'), 'case_notes', ['created_at'], unique=False)
    op.create_index(op.f('ix_case_notes_updated_at'), 'case_notes', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_case_notes_updated_at'), table_name='case_notes')
    op.drop_index(op.f('ix_case_notes_created_at'), table_name='case_notes')
    op.drop_table('case_notes')
    op.drop_index(op.f('ix_cases_updated_at'), table_name='cases')
    op.drop_index(op.f('ix_cases_created_at'), table_name='cases')
    op.drop_table('cases')
    op.drop_index(op.f('ix_cases_version_updated_at'), table_name='cases_version')
    op.drop_index(op.f('ix_cases_version_transaction_id'), table_name='cases_version')
    op.drop_index(op.f('ix_cases_version_operation_type'), table_name='cases_version')
    op.drop_index(op.f('ix_cases_version_end_transaction_id'), table_name='cases_version')
    op.drop_index(op.f('ix_cases_version_created_at'), table_name='cases_version')
    op.drop_table('cases_version')
    op.drop_index(op.f('ix_case_notes_version_updated_at'), table_name='case_notes_version')
    op.drop_index(op.f('ix_case_notes_version_transaction_id'), table_name='case_notes_version')
    op.drop_index(op.f('ix_case_notes_version_operation_type'), table_name='case_notes_version')
    op.drop_index(op.f('ix_case_notes_version_end_transaction_id'), table_name='case_notes_version')
    op.drop_index(op.f('ix_case_notes_version_created_at'), table_name='case_notes_version')
    op.drop_table('case_notes_version')
    # ### end Alembic commands ###
