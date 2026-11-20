import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://enso:enso-dev-only@localhost:5432/enso"
)
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:8080")
