import pytest
from httpx import AsyncClient
from shopAPI.config import settings


@pytest.mark.asyncio
async def test_get_status(
    client: AsyncClient,
) -> None:
    response = await client.get("http://testserver/")
    response_json = response.json()
    assert response.status_code == 200
    assert "name" in response_json
    assert response_json["name"] == settings.PROJECT_NAME
    assert "version" in response_json
    assert response_json["version"] == settings.VERSION
