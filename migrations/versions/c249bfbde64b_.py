"""empty message

Revision ID: c249bfbde64b
Revises: 224ea89b0d62
Create Date: 2024-07-18 19:54:27.792899

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c249bfbde64b'
down_revision = '224ea89b0d62'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('live_stream', schema=None) as batch_op:
        batch_op.drop_column('is_scheduled')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('live_stream', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_scheduled', sa.BOOLEAN(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
