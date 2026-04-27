"""Endpoint tests for the v1.0 Flask app."""


def test_home_page_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"ACEest Fitness" in resp.data


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_version_endpoint(client):
    resp = client.get("/version")
    assert resp.status_code == 200
    assert "version" in resp.get_json()


def test_list_programs_returns_three(client):
    resp = client.get("/programs")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert isinstance(payload, list)
    assert len(payload) == 3
    assert {p["key"] for p in payload} == {"FL", "MG", "BG"}


def test_get_program_by_key_lowercase_accepted(client):
    resp = client.get("/programs/mg")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Muscle Gain (MG)"


def test_get_unknown_program_returns_404(client):
    resp = client.get("/programs/XX")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_calories_endpoint_happy_path(client):
    resp = client.get("/calories?weight=80&program=MG")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body == {"weight": 80.0, "program": "MG", "calories": 2800}


def test_calories_endpoint_bad_weight(client):
    resp = client.get("/calories?weight=-1&program=MG")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_calories_endpoint_unknown_program(client):
    resp = client.get("/calories?weight=70&program=ZZ")
    assert resp.status_code == 400


def test_calories_endpoint_missing_params(client):
    resp = client.get("/calories")
    assert resp.status_code == 400
