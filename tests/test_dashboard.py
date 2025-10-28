from __future__ import annotations

from fastapi.testclient import TestClient


def test_dashboard_widgets(client: TestClient) -> None:
    response = client.get("/dashboard/widgets", headers={"X-User-Role": "admin"})
    assert response.status_code == 200
    payload = response.json()
    keys = {widget["key"] for widget in payload["widgets"]}
    assert {"stock_by_category", "pending_deliveries", "warranties", "assignments", "stock_value", "alerts"} <= keys
