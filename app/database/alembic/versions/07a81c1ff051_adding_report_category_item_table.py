"""adding report category item table

Revision ID: 07a81c1ff051
Revises: 3e16a96e65a8
Create Date: 2021-11-15 17:52:30.541859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07a81c1ff051'
down_revision = '3e16a96e65a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('visit_report_category',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('description', sa.String(length=220), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('visit_report_category')
    # ### end Alembic commands ###
