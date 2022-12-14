"""adding attended details to assistance table

Revision ID: 437f64ef3fae
Revises: 68030bce8db3
Create Date: 2022-01-26 14:23:16.839653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '437f64ef3fae'
down_revision = '68030bce8db3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('assistance', sa.Column('attended_id', sa.Integer(), nullable=False))
    op.add_column('assistance', sa.Column('attended_name', sa.String(length=200), nullable=False))
    op.add_column('assistance', sa.Column('is_attended_relative', sa.Boolean(), server_default='0', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('assistance', 'is_attended_relative')
    op.drop_column('assistance', 'attended_name')
    op.drop_column('assistance', 'attended_id')
    # ### end Alembic commands ###
