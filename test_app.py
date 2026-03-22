import pytest
from app import app, members, classes


@pytest.fixture(autouse=True)
def clear_data():
    """Reset in-memory stores and ID counters before each test."""
    members.clear()
    classes.clear()
    import app as app_module
    app_module._member_id_counter = 1
    app_module._class_id_counter = 1
    yield


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------- HEALTH ----------

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "ACEest" in data["service"]


# ---------- MEMBERS ----------

def test_get_members_empty(client):
    response = client.get("/members")
    assert response.status_code == 200
    assert response.get_json() == []


def test_add_member_success(client):
    payload = {"name": "Alice", "email": "alice@gym.com", "membership_type": "premium"}
    response = client.post("/members", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@gym.com"
    assert data["membership_type"] == "premium"
    assert "id" in data


def test_add_member_default_membership(client):
    payload = {"name": "Bob", "email": "bob@gym.com"}
    response = client.post("/members", json=payload)
    assert response.status_code == 201
    assert response.get_json()["membership_type"] == "basic"


def test_add_member_missing_name(client):
    response = client.post("/members", json={"email": "noname@gym.com"})
    assert response.status_code == 400


def test_add_member_missing_email(client):
    response = client.post("/members", json={"name": "No Email"})
    assert response.status_code == 400


def test_add_member_no_body(client):
    response = client.post("/members", content_type="application/json", data="")
    assert response.status_code == 400


def test_get_member_by_id(client):
    client.post("/members", json={"name": "Carol", "email": "carol@gym.com"})
    response = client.get("/members/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Carol"


def test_get_member_not_found(client):
    response = client.get("/members/999")
    assert response.status_code == 404


def test_get_all_members(client):
    client.post("/members", json={"name": "Dave", "email": "dave@gym.com"})
    client.post("/members", json={"name": "Eve", "email": "eve@gym.com"})
    response = client.get("/members")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_delete_member(client):
    client.post("/members", json={"name": "Frank", "email": "frank@gym.com"})
    response = client.delete("/members/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Frank"
    assert client.get("/members/1").status_code == 404


def test_delete_member_not_found(client):
    response = client.delete("/members/999")
    assert response.status_code == 404


# ---------- CLASSES ----------

def test_get_classes_empty(client):
    response = client.get("/classes")
    assert response.status_code == 200
    assert response.get_json() == []


def test_add_class_success(client):
    payload = {"name": "Yoga", "instructor": "Jane", "schedule": "Mon 9am", "capacity": 15}
    response = client.post("/classes", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Yoga"
    assert data["instructor"] == "Jane"
    assert data["capacity"] == 15


def test_add_class_defaults(client):
    response = client.post("/classes", json={"name": "Zumba", "instructor": "Max"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["schedule"] == "TBD"
    assert data["capacity"] == 20


def test_add_class_missing_name(client):
    response = client.post("/classes", json={"instructor": "Jake"})
    assert response.status_code == 400


def test_add_class_missing_instructor(client):
    response = client.post("/classes", json={"name": "Pilates"})
    assert response.status_code == 400


def test_get_class_by_id(client):
    client.post("/classes", json={"name": "Spin", "instructor": "Lee"})
    response = client.get("/classes/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Spin"


def test_get_class_not_found(client):
    response = client.get("/classes/999")
    assert response.status_code == 404


def test_get_all_classes(client):
    client.post("/classes", json={"name": "Boxing", "instructor": "Ali"})
    client.post("/classes", json={"name": "CrossFit", "instructor": "Sam"})
    response = client.get("/classes")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_member_id_increments(client):
    r1 = client.post("/members", json={"name": "A", "email": "a@a.com"})
    r2 = client.post("/members", json={"name": "B", "email": "b@b.com"})
    assert r1.get_json()["id"] == 1
    assert r2.get_json()["id"] == 2


def test_class_id_increments(client):
    r1 = client.post("/classes", json={"name": "C1", "instructor": "I1"})
    r2 = client.post("/classes", json={"name": "C2", "instructor": "I2"})
    assert r1.get_json()["id"] == 1
    assert r2.get_json()["id"] == 2
