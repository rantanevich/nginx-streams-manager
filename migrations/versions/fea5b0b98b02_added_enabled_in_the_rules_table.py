"""added enabled in the rules table

Revision ID: fea5b0b98b02
Revises: 886daacc411c
Create Date: 2021-05-17 11:22:22.631199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fea5b0b98b02'
down_revision = '886daacc411c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rules', sa.Column('enabled', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('rules', 'enabled')
    # ### end Alembic commands ###
