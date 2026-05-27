import os
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TEST_DB = Path("/tmp/bonnibel_notification_test.db")
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["BONNIBEL_DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["BONNIBEL_JWT_SECRET_KEY"] = "test-secret"

from app.main import app  # noqa: E402
from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.modules.notification.manager import notification_service  # noqa: E402


@pytest.fixture()
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        notification_service.seed_demo_data(db)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client


def auth(user_id: str) -> dict[str, str]:
    return {"X-User-Id": user_id}
