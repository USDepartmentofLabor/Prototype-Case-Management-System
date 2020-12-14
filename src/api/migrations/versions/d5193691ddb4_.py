"""empty message

Revision ID: d5193691ddb4
Revises: bdffe3a13fba
Create Date: 2020-01-14 13:33:54.357559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5193691ddb4'
down_revision = 'bdffe3a13fba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'case_statuses',
        sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('default', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_case_statuses_default'), 'case_statuses', ['default'], unique=False)
    op.add_column('cases', sa.Column('status_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'cases', 'case_statuses', ['status_id'], ['id'])
    op.add_column('cases_version', sa.Column('status_id', sa.Integer(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cases_version', 'status_id')
    op.drop_constraint(None, 'cases', type_='foreignkey')
    op.drop_column('cases', 'status_id')
    op.drop_index(op.f('ix_case_statuses_default'), table_name='case_statuses')
    op.drop_table('case_statuses')
    # ### end Alembic commands ###
