"""empty message

Revision ID: e012a2ad0386
Revises: 58d46109fba0
Create Date: 2021-11-17 10:24:49.504991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e012a2ad0386'
down_revision = '58d46109fba0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('admin',
                    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('user_id')
    )

def downgrade():
    op.drop_table('admin')
