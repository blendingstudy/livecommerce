"""empty message

Revision ID: ff06e678f1f2
Revises: c1b168d71c46
Create Date: 2024-07-24 23:47:30.377622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff06e678f1f2'
down_revision = 'c1b168d71c46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('coupon', schema=None) as batch_op:
        batch_op.add_column(sa.Column('seller_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'user', ['seller_id'], ['id'])

    with op.batch_alter_table('discount', schema=None) as batch_op:
        batch_op.add_column(sa.Column('seller_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'user', ['seller_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('discount', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('seller_id')

    with op.batch_alter_table('coupon', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('seller_id')

    # ### end Alembic commands ###
