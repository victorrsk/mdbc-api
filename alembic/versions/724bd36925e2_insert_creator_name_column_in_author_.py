"""insert creator_name column in author and book table

Revision ID: 724bd36925e2
Revises: c2fdef741180
Create Date: 2026-03-04 20:17:46.988670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '724bd36925e2'
down_revision: Union[str, Sequence[str], None] = 'c2fdef741180'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Para a tabela 'author'
    with op.batch_alter_table('author', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_name', sa.String(), nullable=False))
        batch_op.create_foreign_key('fk_author_user', 'user', ['creator_name'], ['username'])

    # Para a tabela 'book'
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_name', sa.String(), nullable=False))
        batch_op.create_foreign_key('fk_book_user', 'user', ['creator_name'], ['username'])

def downgrade() -> None:
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.drop_constraint('fk_book_user', type_='foreignkey')
        batch_op.drop_column('creator_name')

    with op.batch_alter_table('author', schema=None) as batch_op:
        batch_op.drop_constraint('fk_author_user', type_='foreignkey')
        batch_op.drop_column('creator_name')