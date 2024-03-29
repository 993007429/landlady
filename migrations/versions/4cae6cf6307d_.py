"""empty message

Revision ID: 4cae6cf6307d
Revises: e012a2ad0386
Create Date: 2021-12-22 15:49:57.564604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4cae6cf6307d'
down_revision = 'e012a2ad0386'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admin')
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deploy_type', sa.Enum('python', 'php', name='projectdeploytype'), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.drop_column('deploy_type')

    op.create_table('admin',
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    # ### end Alembic commands ###
