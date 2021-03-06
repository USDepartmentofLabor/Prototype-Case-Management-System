"""add location columns to user model

Revision ID: 7aa3ea85e9e6
Revises: 3f78d37b9b21
Create Date: 2020-04-28 20:15:01.963921

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = '7aa3ea85e9e6'
down_revision = '3f78d37b9b21'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_login_location_altitude', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('last_login_location_altitude_accuracy', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('last_login_location_coordinates', geoalchemy2.types.Geometry(geometry_type='POINT'), nullable=True))
    op.add_column('users', sa.Column('last_login_location_dt', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_login_location_heading', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('last_login_location_position_accuracy', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('last_login_location_speed', sa.Float(), nullable=True))
    op.add_column('users_version', sa.Column('last_login_location_altitude', sa.Float(), autoincrement=False, nullable=True))
    op.add_column('users_version', sa.Column('last_login_location_altitude_accuracy', sa.Float(), autoincrement=False, nullable=True))
    op.add_column('users_version', sa.Column('last_login_location_coordinates', geoalchemy2.types.Geometry(geometry_type='POINT'), autoincrement=False, nullable=True))
    op.add_column('users_version', sa.Column('last_login_location_dt', sa.DateTime(), autoincrement=False, nullable=True))
    op.add_column('users_version', sa.Column('last_login_location_heading', sa.Float(), autoincrement=False, nullable=True))
    op.add_column('users_version', sa.Column('last_login_location_position_accuracy', sa.Float(), autoincrement=False, nullable=True))
    op.add_column('users_version', sa.Column('last_login_location_speed', sa.Float(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users_version', 'last_login_location_speed')
    op.drop_column('users_version', 'last_login_location_position_accuracy')
    op.drop_column('users_version', 'last_login_location_heading')
    op.drop_column('users_version', 'last_login_location_dt')
    op.drop_column('users_version', 'last_login_location_coordinates')
    op.drop_column('users_version', 'last_login_location_altitude_accuracy')
    op.drop_column('users_version', 'last_login_location_altitude')
    op.drop_column('users', 'last_login_location_speed')
    op.drop_column('users', 'last_login_location_position_accuracy')
    op.drop_column('users', 'last_login_location_heading')
    op.drop_column('users', 'last_login_location_dt')
    op.drop_column('users', 'last_login_location_coordinates')
    op.drop_column('users', 'last_login_location_altitude_accuracy')
    op.drop_column('users', 'last_login_location_altitude')
    # ### end Alembic commands ###
