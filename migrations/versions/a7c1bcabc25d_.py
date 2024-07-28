"""empty message

Revision ID: a7c1bcabc25d
Revises: b59eec38a079
Create Date: 2024-07-27 19:21:22.510813

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7c1bcabc25d'
down_revision = 'b59eec38a079'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.drop_constraint('review_product_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'product', ['product_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('review_product_id_fkey', 'live_stream', ['product_id'], ['id'])

    # ### end Alembic commands ###
