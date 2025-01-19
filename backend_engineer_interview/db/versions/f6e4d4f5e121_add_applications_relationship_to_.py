"""Add applications relationship to employee

Revision ID: f6e4d4f5e121
Revises: cd8f3f10f609
Create Date: 2025-01-18 19:20:58.382452

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f6e4d4f5e121"
down_revision = "cd8f3f10f609"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "application",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("leave_start_date", sa.Date(), nullable=False),
        sa.Column("leave_end_date", sa.Date(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employee.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Use batch mode to modify columns for SQLite compatibility
    with op.batch_alter_table("employee", schema=None) as batch_op:
        batch_op.alter_column(
            "first_name",
            existing_type=sa.String(),
            nullable=False,
        )
        batch_op.alter_column(
            "last_name",
            existing_type=sa.String(),
            nullable=False,
        )
        batch_op.alter_column(
            "date_of_birth",
            existing_type=sa.Date(),
            nullable=False,
        )
        batch_op.alter_column(
            "secret",
            existing_type=sa.String(),
            nullable=False,
        )
    # ### end Alembic commands ###


def downgrade():
    # Revert changes in downgrade using batch mode
    with op.batch_alter_table("employee", schema=None) as batch_op:
        batch_op.alter_column(
            "first_name",
            existing_type=sa.String(),
            nullable=True,
        )
        batch_op.alter_column(
            "last_name",
            existing_type=sa.String(),
            nullable=True,
        )
        batch_op.alter_column(
            "date_of_birth",
            existing_type=sa.Date(),
            nullable=True,
        )
        batch_op.alter_column(
            "secret",
            existing_type=sa.String(),
            nullable=True,
        )
    op.drop_table("application")
    # ### end Alembic commands ###