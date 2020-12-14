"""add eps properties

Revision ID: 805050929ef8
Revises: d83d6a1d4dd7
Create Date: 2020-07-07 19:27:42.894547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '805050929ef8'
down_revision = 'd83d6a1d4dd7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('eps_properties',
    sa.Column('property', sa.String(length=64), nullable=False),
    sa.Column('value', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('property')
    )
    op.create_table('eps_properties_version',
    sa.Column('property', sa.String(length=64), autoincrement=False, nullable=False),
    sa.Column('value', sa.Text(), autoincrement=False, nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
    sa.PrimaryKeyConstraint('property', 'transaction_id')
    )
    op.create_index(op.f('ix_eps_properties_version_end_transaction_id'), 'eps_properties_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_eps_properties_version_operation_type'), 'eps_properties_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_eps_properties_version_transaction_id'), 'eps_properties_version', ['transaction_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_eps_properties_version_transaction_id'), table_name='eps_properties_version')
    op.drop_index(op.f('ix_eps_properties_version_operation_type'), table_name='eps_properties_version')
    op.drop_index(op.f('ix_eps_properties_version_end_transaction_id'), table_name='eps_properties_version')
    op.drop_table('eps_properties_version')
    op.drop_table('eps_properties')
    # ### end Alembic commands ###