from __future__ import annotations

from fastapi.testclient import TestClient


def test_assignment_lifecycle(client: TestClient) -> None:
    users = client.get("/users", headers={"X-User-Role": "admin"}).json()
    user_id = users[0]["id"]
    items = client.get("/items", headers={"X-User-Role": "storekeeper"}).json()
    item_id = items[0]["id"]

    order_resp = client.post(
        "/orders",
        json={
            "supplier_id": items[0].get("default_supplier_id") or client.get("/suppliers", headers={"X-User-Role": "storekeeper"}).json()[0]["id"],
            "lines": [
                {"item_id": item_id, "qty": 1, "unit_price": 500, "tax_rate": 0.2},
            ],
        },
        headers={"X-User-Role": "buyer"},
    )
    assert order_resp.status_code == 201, order_resp.text
    order = order_resp.json()

    delivery_resp = client.post(
        f"/orders/{order['id']}/deliveries",
        json={
            "item_id": item_id,
            "serial_numbers": ["SERIAL-XYZ"],
            "warranty_duration_days": 365,
        },
        headers={"X-User-Role": "storekeeper"},
    )
    assert delivery_resp.status_code == 200, delivery_resp.text

    serials = client.get("/serials", params={"status": "in_stock"}, headers={"X-User-Role": "storekeeper"}).json()
    serial_id = next(serial["id"] for serial in serials if serial["serial_number"] == "SERIAL-XYZ")

    assign_resp = client.post(
        "/assignments",
        json={
            "serial_id": serial_id,
            "assignee_user_id": user_id,
            "notes": "Test", 
        },
        headers={"X-User-Role": "storekeeper"},
    )
    assert assign_resp.status_code == 201, assign_resp.text
    assignment = assign_resp.json()
    assert assignment["serial_id"] == serial_id

    return_resp = client.post(f"/assignments/{assignment['id']}/return", headers={"X-User-Role": "storekeeper"})
    assert return_resp.status_code == 200
    assert return_resp.json()["end_date"] is not None
