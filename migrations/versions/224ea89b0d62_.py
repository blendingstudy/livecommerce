"""empty message

Revision ID: 224ea89b0d62
Revises: 06cdcece2d77
Create Date: 2024-07-17 18:00:11.712627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '224ea89b0d62'
down_revision = '06cdcece2d77'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('live_stream', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_scheduled', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('live_stream', schema=None) as batch_op:
        batch_op.drop_column('is_scheduled')

    # ### end Alembic commands ###
