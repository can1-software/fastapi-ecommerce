from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "003_rename_image"
down_revision: str | None = "002_categories_products"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("products", "image_url", new_column_name="image")


def downgrade() -> None:
    op.alter_column("products", "image", new_column_name="image_url")
