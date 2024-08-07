"""empty message

Revision ID: b59eec38a079
Revises: 547c98338d50
Create Date: 2024-07-27 18:43:09.256728

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b59eec38a079'
down_revision = '547c98338d50'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_id', sa.Integer(), nullable=False))
        batch_op.drop_constraint('review_live_stream_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'live_stream', ['product_id'], ['id'])
        batch_op.drop_column('live_stream_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.add_column(sa.Column('live_stream_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('review_live_stream_id_fkey', 'live_stream', ['live_stream_id'], ['id'])
        batch_op.drop_column('product_id')

    # ### end Alembic commands ###
