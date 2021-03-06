"""add source type and case to responses

Revision ID: bdffe3a13fba
Revises: 2508b1844686
Create Date: 2019-12-31 17:51:07.495969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdffe3a13fba'
down_revision = '2508b1844686'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('survey_responses', sa.Column('case_id', sa.Integer(), nullable=True))
    op.add_column('survey_responses', sa.Column('source_type', sa.String()))
    op.execute("UPDATE survey_responses set source_type = 'Standalone';")
    op.alter_column('survey_responses', 'source_type', nullable=False)
    op.create_foreign_key(None, 'survey_responses', 'cases', ['case_id'], ['id'])
    op.add_column('survey_responses_version', sa.Column('case_id', sa.Integer(), autoincrement=False, nullable=True))
    op.add_column('survey_responses_version', sa.Column('source_type', sa.String(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('survey_responses_version', 'source_type')
    op.drop_column('survey_responses_version', 'case_id')
    op.drop_constraint(None, 'survey_responses', type_='foreignkey')
    op.drop_column('survey_responses', 'source_type')
    op.drop_column('survey_responses', 'case_id')
    # ### end Alembic commands ###
