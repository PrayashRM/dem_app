"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# ─── Revision Identifiers ─────────────────────────────────────────────────────
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ─── Define ENUM outside functions so both upgrade and downgrade can use it ───
userrole_enum = ENUM("user", "admin", name="userrole", create_type=False)


def upgrade() -> None:
    """Create users and products tables with all constraints and indexes."""

    conn = op.get_bind()

    # ── Create ENUM type safely — only if it does not already exist ───────────
    conn.execute(sa.text(
        "DO $$ BEGIN "
        "CREATE TYPE userrole AS ENUM ('user', 'admin'); "
        "EXCEPTION WHEN duplicate_object THEN null; "
        "END $$;"
    ))

    # ── Create users table ────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.String(36),
            nullable=False,
            comment="UUID primary key"
        ),
        sa.Column(
            "email",
            sa.String(255),
            nullable=False,
            comment="Unique user email address"
        ),
        sa.Column(
            "full_name",
            sa.String(100),
            nullable=False,
            comment="User full name"
        ),
        sa.Column(
            "hashed_password",
            sa.String(255),
            nullable=False,
            comment="bcrypt hashed password"
        ),
        sa.Column(
            "role",
            userrole_enum,
            nullable=False,
            server_default="user",
            comment="User role for RBAC"
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
            comment="Soft disable flag"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            comment="Record creation timestamp"
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            comment="Record last update timestamp"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    # ── Users indexes ─────────────────────────────────────────────────────────
    op.create_index("ix_users_id",        "users", ["id"])
    op.create_index("ix_users_email",     "users", ["email"])
    op.create_index("ix_users_role",      "users", ["role"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    # ── Create products table ─────────────────────────────────────────────────
    op.create_table(
        "products",
        sa.Column(
            "id",
            sa.String(36),
            nullable=False,
            comment="UUID primary key"
        ),
        sa.Column(
            "name",
            sa.String(100),
            nullable=False,
            comment="Product name"
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
            comment="Product description"
        ),
        sa.Column(
            "price",
            sa.Float(),
            nullable=False,
            comment="Product price in base currency"
        ),
        sa.Column(
            "stock",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
            comment="Available stock quantity"
        ),
        sa.Column(
            "category",
            sa.String(50),
            nullable=True,
            comment="Product category label"
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
            comment="Soft delete flag"
        ),
        sa.Column(
            "created_by",
            sa.String(36),
            nullable=False,
            comment="FK to users table"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            comment="Record creation timestamp"
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            comment="Record last update timestamp"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_products"),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name="fk_products_created_by_users",
            ondelete="CASCADE"
        ),
    )

    # ── Products indexes ──────────────────────────────────────────────────────
    op.create_index("ix_products_id",         "products", ["id"])
    op.create_index("ix_products_name",       "products", ["name"])
    op.create_index("ix_products_category",   "products", ["category"])
    op.create_index("ix_products_created_by", "products", ["created_by"])

    # Composite indexes for common query patterns
    op.create_index(
        "idx_products_name_category",
        "products",
        ["name", "category"]
    )
    op.create_index(
        "idx_products_active_created",
        "products",
        ["is_active", "created_at"]
    )
    op.create_index(
        "idx_products_active_price",
        "products",
        ["is_active", "price"]
    )

    # ── updated_at auto-update trigger ────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    op.execute("""
        CREATE TRIGGER trigger_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
        CREATE TRIGGER trigger_products_updated_at
        BEFORE UPDATE ON products
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Drop all tables, indexes, triggers, and types created in upgrade."""

    # ── Drop triggers ─────────────────────────────────────────────────────────
    op.execute("DROP TRIGGER IF EXISTS trigger_products_updated_at ON products;")
    op.execute("DROP TRIGGER IF EXISTS trigger_users_updated_at ON users;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # ── Drop products indexes ─────────────────────────────────────────────────
    op.drop_index("idx_products_active_price",  table_name="products")
    op.drop_index("idx_products_active_created", table_name="products")
    op.drop_index("idx_products_name_category", table_name="products")
    op.drop_index("ix_products_created_by",     table_name="products")
    op.drop_index("ix_products_category",       table_name="products")
    op.drop_index("ix_products_name",           table_name="products")
    op.drop_index("ix_products_id",             table_name="products")
    op.drop_table("products")

    # ── Drop users indexes ────────────────────────────────────────────────────
    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_index("ix_users_role",      table_name="users")
    op.drop_index("ix_users_email",     table_name="users")
    op.drop_index("ix_users_id",        table_name="users")
    op.drop_table("users")

    # ── Drop ENUM type safely ─────────────────────────────────────────────────
    op.execute("DROP TYPE IF EXISTS userrole;")