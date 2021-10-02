"""init

Revision ID: 86800f0880ef
Revises: 
Create Date: 2021-10-02 18:42:00.975844

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86800f0880ef'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String, unique=True),
        sa.Column('email', sa.String, unique=True),
        sa.Column('password', sa.Text, nullable=True),
        sa.Column('is_staff', sa.String, default=False),
        sa.Column('is_active', sa.String, default=True),
    )

    op.create_table(
        'orders',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('order_status', sa.String, default="PENDING"),
        sa.Column('pizza_size', sa.String, default="SMALL"),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'],),
    )


def downgrade():
    op.drop_table('orders')
    op.drop_table('user')
