from __future__ import annotations

from fastapi.testclient import TestClient


def test_upload_and_download_file(client: TestClient) -> None:
    orders = client.get("/orders", headers={"X-User-Role": "buyer"}).json()
    assert orders, "Expected at least one order from seed data"
    order_id = orders[0]["id"]

    payload = {"entity_type": "order", "entity_id": str(order_id)}
    content = b"%PDF-1.4 demo"
    response = client.post(
        "/files",
        data=payload,
        files={"attachment": ("test.pdf", content, "application/pdf")},
        headers={"X-User-Role": "buyer"},
    )
    assert response.status_code == 201, response.text
    file_info = response.json()
    assert file_info["filename"] == "test.pdf"
    assert file_info["size"] == len(content)
    assert file_info["entity_type"] == "order"
    assert file_info["entity_id"] == order_id

    download = client.get(file_info["download_url"], headers={"X-User-Role": "buyer"})
    assert download.status_code == 200, download.text
    assert download.content == content

    files_list = client.get(
        "/files",
        params={"entity_type": "order", "entity_id": order_id},
        headers={"X-User-Role": "buyer"},
    ).json()
    assert any(file_row["id"] == file_info["id"] for file_row in files_list)

    order_details = client.get(f"/orders/{order_id}", headers={"X-User-Role": "buyer"}).json()
    assert any(file_row["id"] == file_info["id"] for file_row in order_details["files"])
