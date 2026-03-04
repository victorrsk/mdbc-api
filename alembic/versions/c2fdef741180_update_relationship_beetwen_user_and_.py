"""update relationship beetwen user and book

Revision ID: c2fdef741180
Revises: b9546b1721de
Create Date: 2026-03-04 19:52:41.377645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2fdef741180'
down_revision: Union[str, Sequence[str], None] = 'b9546b1721de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:

    with op.batch_alter_table("author") as batch_op:

        # remover FK antiga (created_by_id)
        batch_op.drop_column("created_by_id")

        # remover coluna antiga

        # adicionar nova coluna
        batch_op.add_column(
            sa.Column("creator_id", sa.Integer(), nullable=False)
        )

        # criar nova FK
        batch_op.create_foreign_key(
            "creator_id",
            "user",
            ["creator_id"],
            ["id"],
            ondelete="CASCADE"
        )


    # BOOK
    with op.batch_alter_table("book") as batch_op:

        batch_op.add_column(
            sa.Column("creator_id", sa.Integer(), nullable=False)
        )

        batch_op.create_foreign_key(
            "creator_id",
            "user",
            ["creator_id"],
            ["id"],
            ondelete="CASCADE"
        )


def downgrade() -> None:

    with op.batch_alter_table("book") as batch_op:
        batch_op.drop_constraint("creator_id", type_="foreignkey")
        batch_op.drop_column("creator_id")

    with op.batch_alter_table("author") as batch_op:
        batch_op.drop_constraint("creator_id", type_="foreignkey")
        batch_op.drop_column("creator_id")
        batch_op.add_column(
            sa.Column("created_by_id", sa.Integer(), nullable=False)
        )
