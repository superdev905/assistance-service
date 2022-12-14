"""adding report targ

Revision ID: 1396372aedb2
Revises: 724938ea445d
Create Date: 2021-11-03 14:59:41.814299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1396372aedb2'
down_revision = '724938ea445d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('report_target',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('contact_id', sa.Integer(), nullable=False),
    sa.Column('visit_id', sa.Integer(), nullable=False),
    sa.Column('contact_names', sa.String(length=250), nullable=False),
    sa.Column('contact_email', sa.String(length=100), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['visit_id'], ['visit.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('report_target')
    # ### end Alembic commands ###
