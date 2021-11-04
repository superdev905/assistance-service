"""renaming report target visit id

Revision ID: 3747450267f3
Revises: b6e415ed9a96
Create Date: 2021-11-03 16:17:00.703947

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3747450267f3'
down_revision = 'b6e415ed9a96'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('report_target', sa.Column('visit_report_id', sa.Integer(), nullable=False))
    op.drop_constraint('report_target_visit_id_fkey', 'report_target', type_='foreignkey')
    op.create_foreign_key(None, 'report_target', 'visit_report', ['visit_report_id'], ['id'], ondelete='CASCADE')
    op.drop_column('report_target', 'visit_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('report_target', sa.Column('visit_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'report_target', type_='foreignkey')
    op.create_foreign_key('report_target_visit_id_fkey', 'report_target', 'visit_report', ['visit_id'], ['id'], ondelete='CASCADE')
    op.drop_column('report_target', 'visit_report_id')
    # ### end Alembic commands ###