"""empty message

Revision ID: 30d7d5f5c184
Revises: dc86fa553ae8
Create Date: 2022-04-05 23:27:18.693059

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30d7d5f5c184'
down_revision = 'dc86fa553ae8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('aisle_1', sa.String(length=500), nullable=True))
    op.create_unique_constraint(None, 'user', ['aisle_1'])
    op.drop_column('user', 'items')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('items', sa.VARCHAR(length=500), nullable=True))
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_column('user', 'aisle_1')
    # ### end Alembic commands ###
