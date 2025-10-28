from __future__ import annotations

from fastapi.testclient import TestClient


def _create_order(client: TestClient) -> int:
    suppliers = client.get("/suppliers", headers={"X-User-Role": "buyer"}).json()
    supplier_id = suppliers[0]["id"]
    items = client.get("/items", headers={"X-User-Role": "buyer"}).json()
    item_id = items[0]["id"]
    response = client.post(
        "/orders",
        json={
            "supplier_id": supplier_id,
            "internal_ref": "TEST-ORDER",
            "lines": [
                {"item_id": item_id, "qty": 1, "unit_price": 1000, "tax_rate": 0.2},
            ],
        },
        headers={"X-User-Role": "buyer"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_order_status_flow(client: TestClient) -> None:
    order_id = _create_order(client)

    for status in ("internal", "ordered", "delivered"):
        response = client.patch(
            f"/orders/{order_id}/status",
            json={"status": status},
            headers={"X-User-Role": "buyer"},
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == status

    order = client.get(f"/orders/{order_id}", headers={"X-User-Role": "buyer"}).json()
    assert order["status"] == "delivered"
