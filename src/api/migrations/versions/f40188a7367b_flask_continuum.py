"""flask-continuum

Revision ID: f40188a7367b
Revises: 5e639c44bf54
Create Date: 2019-12-18 05:28:59.248836

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f40188a7367b'
down_revision = '5e639c44bf54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('survey_responses_version',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('structure', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('survey_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('status_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('is_archived', sa.Boolean(), autoincrement=False, nullable=True),
    sa.Column('mongo_id', sa.String(length=64), autoincrement=False, nullable=True),
    sa.Column('created_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('updated_at', sa.DateTime(), autoincrement=False, nullable=True),
    sa.Column('created_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('updated_by_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_survey_responses_version_created_at'), 'survey_responses_version', ['created_at'], unique=False)
    op.create_index(op.f('ix_survey_responses_version_end_transaction_id'), 'survey_responses_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_survey_responses_version_operation_type'), 'survey_responses_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_survey_responses_version_transaction_id'), 'survey_responses_version', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_survey_responses_version_updated_at'), 'survey_responses_version', ['updated_at'], unique=False)
    op.create_table('transaction',
    sa.Column('issued_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('remote_addr', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transaction')
    op.drop_index(op.f('ix_survey_responses_version_updated_at'), table_name='survey_responses_version')
    op.drop_index(op.f('ix_survey_responses_version_transaction_id'), table_name='survey_responses_version')
    op.drop_index(op.f('ix_survey_responses_version_operation_type'), table_name='survey_responses_version')
    op.drop_index(op.f('ix_survey_responses_version_end_transaction_id'), table_name='survey_responses_version')
    op.drop_index(op.f('ix_survey_responses_version_created_at'), table_name='survey_responses_version')
    op.drop_table('survey_responses_version')
    # ### end Alembic commands ###