"""More API-level integration tests -- budgets and savings goals."""


def test_create_budget_and_see_it_in_list(client):
    create_resp = client.post("/budgets", json={
        "category": "food", "amount": 2000, "month": "2026-08-01",
    })
    assert create_resp.status_code == 201
    assert create_resp.json()["status"] == "normal"

    list_resp = client.get("/budgets?month=2026-08-01")
    assert len(list_resp.json()) == 1


def test_duplicate_budget_same_category_month_returns_409(client):
    payload = {"category": "shopping", "amount": 1000, "month": "2026-08-01"}
    first = client.post("/budgets", json=payload)
    assert first.status_code == 201

    second = client.post("/budgets", json=payload)
    assert second.status_code == 409


def test_budget_status_reflects_actual_spending(client):
    client.post("/budgets", json={"category": "food", "amount": 1000, "month": "2026-08-01"})
    client.post("/transactions", json={
        "amount": 950, "category": "food", "date": "2026-08-05",
        "payment_method": "upi", "type": "need",
    })
    budgets = client.get("/budgets?month=2026-08-01").json()
    assert budgets[0]["status"] == "critical"  # 95% used


def test_create_goal_and_contribute(client):
    create_resp = client.post("/goals", json={
        "name": "Laptop", "target_amount": 5000, "current_amount": 0,
        "deadline": "2026-12-01", "priority": "high",
    })
    assert create_resp.status_code == 201
    goal_id = create_resp.json()["id"]
    assert create_resp.json()["is_completed"] is False

    contribute_resp = client.post(f"/goals/{goal_id}/contribute", json={"amount": 5000})
    assert contribute_resp.status_code == 200
    assert contribute_resp.json()["is_completed"] is True
    assert contribute_resp.json()["progress_percentage"] == 100.0


def test_goal_rejects_zero_target_amount(client):
    response = client.post("/goals", json={
        "name": "Bad goal", "target_amount": 0, "current_amount": 0, "priority": "low",
    })
    assert response.status_code == 422


def test_other_user_cannot_contribute_to_your_goal(client, other_user_headers):
    create_resp = client.post("/goals", json={
        "name": "My private goal", "target_amount": 1000, "current_amount": 0, "priority": "medium",
    })
    goal_id = create_resp.json()["id"]

    other_attempt = client.post(
        f"/goals/{goal_id}/contribute", json={"amount": 1000}, headers=other_user_headers
    )
    assert other_attempt.status_code == 404
