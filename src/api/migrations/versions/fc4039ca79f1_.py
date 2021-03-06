"""empty message

Revision ID: fc4039ca79f1
Revises: 914ed6d0c731
Create Date: 2019-10-18 20:28:09.699926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc4039ca79f1'
down_revision = '914ed6d0c731'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('survey_response_statuses',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('survey_responses', sa.Column('created_by_id', sa.Integer(), nullable=False))
    op.add_column('survey_responses', sa.Column('status_id', sa.Integer(), nullable=False))
    op.add_column('survey_responses', sa.Column('updated_by_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'survey_responses', 'survey_response_statuses', ['status_id'], ['id'])
    op.create_foreign_key(None, 'survey_responses', 'users', ['created_by_id'], ['id'])
    op.create_foreign_key(None, 'survey_responses', 'users', ['updated_by_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'survey_responses', type_='foreignkey')
    op.drop_constraint(None, 'survey_responses', type_='foreignkey')
    op.drop_constraint(None, 'survey_responses', type_='foreignkey')
    op.drop_column('survey_responses', 'updated_by_id')
    op.drop_column('survey_responses', 'status_id')
    op.drop_column('survey_responses', 'created_by_id')
    op.drop_table('survey_response_statuses')
    # ### end Alembic commands ###
