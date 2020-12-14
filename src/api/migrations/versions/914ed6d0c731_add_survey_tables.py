"""add_survey_tables

Revision ID: 914ed6d0c731
Revises: d7530a372eef
Create Date: 2019-10-08 17:34:38.905869

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '914ed6d0c731'
down_revision = 'd7530a372eef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('error_codes',
    sa.Column('code', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('message', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('surveys',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('structure', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_surveys_created_at'), 'surveys', ['created_at'], unique=False)
    op.create_index(op.f('ix_surveys_name'), 'surveys', ['name'], unique=True)
    op.create_index(op.f('ix_surveys_updated_at'), 'surveys', ['updated_at'], unique=False)
    op.create_table('survey_responses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('structure', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('survey_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['survey_id'], ['surveys.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_survey_responses_created_at'), 'survey_responses', ['created_at'], unique=False)
    op.create_index(op.f('ix_survey_responses_updated_at'), 'survey_responses', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_survey_responses_updated_at'), table_name='survey_responses')
    op.drop_index(op.f('ix_survey_responses_created_at'), table_name='survey_responses')
    op.drop_table('survey_responses')
    op.drop_index(op.f('ix_surveys_updated_at'), table_name='surveys')
    op.drop_index(op.f('ix_surveys_name'), table_name='surveys')
    op.drop_index(op.f('ix_surveys_created_at'), table_name='surveys')
    op.drop_table('surveys')
    op.drop_table('error_codes')
    # ### end Alembic commands ###