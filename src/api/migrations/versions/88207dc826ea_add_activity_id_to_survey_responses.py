"""add activity_id to survey_responses

Revision ID: 88207dc826ea
Revises: bea0a35e6c0a
Create Date: 2020-09-29 17:58:00.934547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88207dc826ea'
down_revision = 'bea0a35e6c0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_activities_created_location_coordinates', table_name='activities')
    op.drop_index('idx_activities_updated_location_coordinates', table_name='activities')
    op.drop_index('idx_activities_version_created_location_coordinates', table_name='activities_version')
    op.drop_index('idx_activities_version_updated_location_coordinates', table_name='activities_version')
    op.add_column('survey_responses', sa.Column('activity_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'survey_responses', 'activities', ['activity_id'], ['id'])
    op.add_column('survey_responses_version', sa.Column('activity_id', sa.Integer(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('survey_responses_version', 'activity_id')
    op.drop_constraint(None, 'survey_responses', type_='foreignkey')
    op.drop_column('survey_responses', 'activity_id')
    op.create_index('idx_activities_version_updated_location_coordinates', 'activities_version', ['updated_location_coordinates'], unique=False)
    op.create_index('idx_activities_version_created_location_coordinates', 'activities_version', ['created_location_coordinates'], unique=False)
    op.create_index('idx_activities_updated_location_coordinates', 'activities', ['updated_location_coordinates'], unique=False)
    op.create_index('idx_activities_created_location_coordinates', 'activities', ['created_location_coordinates'], unique=False)
    # ### end Alembic commands ###
