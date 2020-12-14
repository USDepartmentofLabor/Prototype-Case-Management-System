"""add custom fields

Revision ID: a559e585c396
Revises: f003e834bfdb
Create Date: 2020-05-11 14:50:12.839270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a559e585c396'
down_revision = 'f003e834bfdb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('custom_fields',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('field_type', sa.String(length=16), nullable=False),
    sa.Column('selections', sa.ARRAY(sa.Text()), nullable=True),
    sa.Column('validation_rules', sa.ARRAY(sa.Text()), nullable=True),
    sa.Column('model_type', sa.String(), nullable=True),
    sa.Column('model_id', sa.Integer(), nullable=True),
    sa.Column('custom_section_id', sa.Integer(), nullable=True),
    sa.Column('help_text', sa.Text(), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=False),
    sa.Column('updated_by_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_custom_fields_created_at'), 'custom_fields', ['created_at'], unique=False)
    op.create_index(op.f('ix_custom_fields_name'), 'custom_fields', ['name'], unique=True)
    op.create_index(op.f('ix_custom_fields_updated_at'), 'custom_fields', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_custom_fields_updated_at'), table_name='custom_fields')
    op.drop_index(op.f('ix_custom_fields_name'), table_name='custom_fields')
    op.drop_index(op.f('ix_custom_fields_created_at'), table_name='custom_fields')
    op.drop_table('custom_fields')
    # ### end Alembic commands ###
