"""empty message

Revision ID: fe6dd03d0887
Revises: d0f1531bc014
Create Date: 2024-06-24 20:11:24.828083

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe6dd03d0887'
down_revision = 'd0f1531bc014'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('live_stream',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('is_live', sa.Boolean(), nullable=True),
    sa.Column('viewer_count', sa.Integer(), nullable=True),
    sa.Column('stream_url', sa.String(length=200), nullable=True),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['seller_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('live_stream_comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('live_stream_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['live_stream_id'], ['live_stream.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('live_stream_products',
    sa.Column('live_stream_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['live_stream_id'], ['live_stream.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('live_stream_id', 'product_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('live_stream_products')
    op.drop_table('live_stream_comment')
    op.drop_table('live_stream')
    # ### end Alembic commands ###