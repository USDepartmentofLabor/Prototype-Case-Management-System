"""add deleted object log

Revision ID: 5e639c44bf54
Revises: b335ac8b2345
Create Date: 2019-12-17 23:48:59.801195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e639c44bf54'
down_revision = 'b335ac8b2345'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('deleted_object_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('deleted_object_code', sa.String(), nullable=False),
    sa.Column('deleted_object_id', sa.Integer(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_by_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['deleted_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deleted_object_log_deleted_at'), 'deleted_object_log', ['deleted_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_deleted_object_log_deleted_at'), table_name='deleted_object_log')
    op.drop_table('deleted_object_log')
    # ### end Alembic commands ###