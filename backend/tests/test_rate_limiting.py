"""
Confirms the rate limiter actually engages -- not just that the decorator
is present, but that hammering an endpoint past its limit really returns
429, and that a normal endpoint without a tight override still works.
"""


def test_health_endpoint_not_rate_limited_at_normal_volume(client):
    # /health has no per-route limit override -- well under the 60/min
    # default, this should never trip.
    for _ in range(10):
        response = client.get("/health")
        assert response.status_code == 200


def test_affordability_check_trips_rate_limit_when_hammered(client):
    payload = {"item_name": "Test item", "amount": 100}
    statuses = []
    for _ in range(35):  # limit is 30/minute
        response = client.post("/ai/affordability-check", json=payload)
        statuses.append(response.status_code)

    assert 429 in statuses, "Expected at least one 429 after exceeding 30/minute"
    # Everything before the limit tripped should have succeeded normally
    assert statuses[0] == 200
