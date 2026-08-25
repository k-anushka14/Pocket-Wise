"""
API-level integration tests for /transactions -- exercising real routes
through a real (in-memory) database, not just the pure logic functions.
"""
from decimal import Decimal


def test_health_check_no_auth_needed(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_transaction(client):
    create_resp = client.post("/transactions", json={
        "amount": 450, "category": "food", "description": "Pizza",
        "date": "2026-08-20", "payment_method": "upi", "type": "want",
    })
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert body["amount"] == "450.00" or float(body["amount"]) == 450
    assert body["category"] == "food"

    list_resp = client.get("/transactions")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["description"] == "Pizza"


def test_create_transaction_rejects_negative_amount(client):
    response = client.post("/transactions", json={
        "amount": -50, "category": "food", "date": "2026-08-20",
        "payment_method": "upi", "type": "want",
    })
    assert response.status_code == 422


def test_create_transaction_rejects_invalid_category(client):
    response = client.post("/transactions", json={
        "amount": 50, "category": "not_a_real_category", "date": "2026-08-20",
        "payment_method": "upi", "type": "want",
    })
    assert response.status_code == 422


def test_update_and_delete_transaction(client):
    create_resp = client.post("/transactions", json={
        "amount": 100, "category": "cafe", "date": "2026-08-20",
        "payment_method": "cash", "type": "want",
    })
    txn_id = create_resp.json()["id"]

    update_resp = client.put(f"/transactions/{txn_id}", json={"amount": 150})
    assert update_resp.status_code == 200
    assert float(update_resp.json()["amount"]) == 150

    delete_resp = client.delete(f"/transactions/{txn_id}")
    assert delete_resp.status_code == 204

    list_resp = client.get("/transactions")
    assert list_resp.json() == []


def test_get_nonexistent_transaction_returns_404(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/transactions/{fake_id}")
    assert response.status_code == 404


def test_transactions_filter_by_category(client):
    client.post("/transactions", json={
        "amount": 100, "category": "food", "date": "2026-08-20",
        "payment_method": "upi", "type": "need",
    })
    client.post("/transactions", json={
        "amount": 200, "category": "shopping", "date": "2026-08-20",
        "payment_method": "upi", "type": "want",
    })
    response = client.get("/transactions?category=food")
    items = response.json()
    assert len(items) == 1
    assert items[0]["category"] == "food"


# --- Cross-user isolation: the core "never leak another user's data" guarantee ---

def test_user_cannot_see_another_users_transactions(client, other_user_headers):
    client.post("/transactions", json={
        "amount": 999, "category": "shopping", "date": "2026-08-20",
        "payment_method": "upi", "type": "want",
    })
    # Same client, same in-memory DB, different user via header
    other_list = client.get("/transactions", headers=other_user_headers)
    assert other_list.json() == []


def test_user_cannot_fetch_another_users_transaction_by_id(client, other_user_headers):
    create_resp = client.post("/transactions", json={
        "amount": 500, "category": "food", "date": "2026-08-20",
        "payment_method": "cash", "type": "need",
    })
    txn_id = create_resp.json()["id"]

    other_get = client.get(f"/transactions/{txn_id}", headers=other_user_headers)
    assert other_get.status_code == 404  # not 403 -- never confirms it exists


def test_user_cannot_delete_another_users_transaction(client, other_user_headers):
    create_resp = client.post("/transactions", json={
        "amount": 500, "category": "food", "date": "2026-08-20",
        "payment_method": "cash", "type": "need",
    })
    txn_id = create_resp.json()["id"]

    other_delete = client.delete(f"/transactions/{txn_id}", headers=other_user_headers)
    assert other_delete.status_code == 404

    # Original owner can still see it -- confirms the other user's failed
    # delete attempt didn't silently succeed against the wrong row.
    still_there = client.get(f"/transactions/{txn_id}")
    assert still_there.status_code == 200
