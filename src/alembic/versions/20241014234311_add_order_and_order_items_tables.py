"""Add order and order_items tables

Revision ID: e34cf6b38c62
Revises: c566a38fb1a6
Create Date: 2024-10-14 23:43:11.014727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'e34cf6b38c62'
down_revision: Union[str, None] = 'c566a38fb1a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order',
    sa.Column('creation_date', sa.DateTime(), nullable=False),
    sa.Column('status', sa.Enum('created', 'processing', 'shipped', 'delivered', 'canceled', name='orderstatus'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_id'), 'order', ['id'], unique=False)
    op.create_table('order_item',
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('order_id', sa.Uuid(), nullable=True),
    sa.Column('product_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_item_id'), 'order_item', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_order_item_id'), table_name='order_item')
    op.drop_table('order_item')
    op.drop_index(op.f('ix_order_id'), table_name='order')
    op.drop_table('order')
    # ### end Alembic commands ###
