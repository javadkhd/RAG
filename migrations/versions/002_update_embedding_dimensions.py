"""Update embeddings.vector column from vector(1536) to vector(1024) to match BAAI/bge-m3 output dimensions."""

from alembic import op

revision: str = "002_update_embedding_dimensions"
down_revision: str = "001_initial"
branch_labels: tuple[str] | None = None
depends_on: tuple[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE embeddings ALTER COLUMN vector TYPE vector(1024)")


def downgrade() -> None:
    op.execute("ALTER TABLE embeddings ALTER COLUMN vector TYPE vector(1536)")
