"""rules table

Revision ID: 886daacc411c
Revises: 
Create Date: 2021-05-16 23:59:39.941243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '886daacc411c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('src_port', sa.Integer(), nullable=True),
    sa.Column('dst_ip', sa.String(length=16), nullable=True),
    sa.Column('dst_port', sa.Integer(), nullable=True),
    sa.Column('comment', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rules_src_port'), 'rules', ['src_port'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_rules_src_port'), table_name='rules')
    op.drop_table('rules')
    # ### end Alembic commands ###