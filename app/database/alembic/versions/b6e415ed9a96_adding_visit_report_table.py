"""adding visit report table

Revision ID: b6e415ed9a96
Revises: 1396372aedb2
Create Date: 2021-11-03 15:50:01.780104

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6e415ed9a96'
down_revision = '1396372aedb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('visit_report',
                    sa.Column('id', sa.Integer(),
                              autoincrement=True, nullable=False),
                    sa.Column('user_name', sa.String(
                        length=250), nullable=False),
                    sa.Column('user_phone', sa.String(
                        length=9), nullable=True),
                    sa.Column('user_email', sa.String(
                        length=100), nullable=False),
                    sa.Column('observations', sa.String(
                        length=800), nullable=False),
                    sa.Column('relevant', sa.String(
                        length=800), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('report_url', sa.String(
                        length=255), nullable=False),
                    sa.Column('report_key', sa.String(
                        length=255), nullable=False),
                    sa.Column('create_date', sa.DateTime(
                        timezone=True), nullable=False, server_default=sa.text('now()')),
                    sa.Column('visit_id', sa.Integer(), nullable=False),
                    sa.Column('created_by', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('update_at', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['visit_id'], ['visit.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.create_unique_constraint(None, 'report_target', ['id'])
    op.drop_constraint('report_target_visit_id_fkey',
                       'report_target', type_='foreignkey')
    op.create_foreign_key(None, 'report_target', 'visit_report', [
                          'visit_id'], ['id'], ondelete='CASCADE')
    op.drop_column('visit', 'report_key')
    op.drop_column('visit', 'report_url')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('visit', sa.Column('report_url', sa.VARCHAR(
        length=255), autoincrement=False, nullable=True))
    op.add_column('visit', sa.Column('report_key', sa.VARCHAR(
        length=255), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'report_target', type_='foreignkey')
    op.create_foreign_key('report_target_visit_id_fkey', 'report_target', 'visit', [
                          'visit_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'report_target', type_='unique')
    op.drop_table('visit_report')
    # ### end Alembic commands ###