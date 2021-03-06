"""add activity definitions surveys relationship

Revision ID: a30c6e4c46ce
Revises: b196a337f956
Create Date: 2020-09-24 14:27:11.823712

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a30c6e4c46ce'
down_revision = 'b196a337f956'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('activity_definitions_surveys',
                    sa.Column('activity_definition_id', sa.Integer(), nullable=False),
                    sa.Column('survey_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['activity_definition_id'], ['activity_definitions.id'], ),
                    sa.ForeignKeyConstraint(['survey_id'], ['surveys.id'], ),
                    sa.PrimaryKeyConstraint('activity_definition_id', 'survey_id')
                    )
    op.create_index(op.f('ix_activity_definitions_surveys_activity_definition_id'), 'activity_definitions_surveys',
                    ['activity_definition_id'], unique=False)
    op.create_index(op.f('ix_activity_definitions_surveys_survey_id'), 'activity_definitions_surveys', ['survey_id'],
                    unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_activity_definitions_surveys_survey_id'), table_name='activity_definitions_surveys')
    op.drop_index(op.f('ix_activity_definitions_surveys_activity_definition_id'),
                  table_name='activity_definitions_surveys')
    op.drop_table('activity_definitions_surveys')
    # ### end Alembic commands ###
