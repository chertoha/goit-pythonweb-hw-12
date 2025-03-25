from datetime import datetime, timedelta

contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "123456789",
        "birth_date": "1990-05-15"
    }


def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert "id" in data

def test_create_contact_email_exists(client, get_token):
    client.post("/api/contacts", json=contact_data, headers={"Authorization": f"Bearer {get_token}"})

    contact_data_with_existing_email = {
        **contact_data,
        "email": "john.doe@example.com",
    }
    response = client.post(
        "/api/contacts",
        json=contact_data_with_existing_email,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Contact with email=john.doe@example.com already exists"


def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert "id" in data

def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    response = client.get("/api/contacts", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]

def test_update_contact(client, get_token):
    contact_update_data = {
        "first_name": "John Updated",
        "email": "john.updated@example.com",
        "phone": "987654321",
        "birth_date": "1990-05-15"
    }
    response = client.patch(
        "/api/contacts/1",
        json=contact_update_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "John Updated"
    assert data["email"] == "john.updated@example.com"
    assert "id" in data

def test_update_contact_not_found(client, get_token):
    contact_update_data = {
        "first_name": "Nonexistent Contact",
        "email": "nonexistent@example.com",
        "phone": "000000000",
        "birth_date": "1990-05-15"
    }
    response = client.patch(
        "/api/contacts/999",
        json=contact_update_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_update_contact_email_exists(client, get_token):
    client.post("/api/contacts", json=contact_data, headers={"Authorization": f"Bearer {get_token}"})
    contact_data_to_update = {"email": "john.doe@example.com"}
    response = client.patch(
        "/api/contacts/2",
        json=contact_data_to_update,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Contact with email=john.doe@example.com already exists"




def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "John Updated"
    assert "id" in data

def test_delete_contact_not_found(client, get_token):
    response = client.delete(
        "/api/contacts/999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"

def test_get_upcoming_birthdays(client, get_token):
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")

    contact = {**contact_data, "birth_date":tomorrow_str, "email":"birth@gmail.com"}
    res = client.post("/api/contacts", json=contact, headers={"Authorization": f"Bearer {get_token}"})
    print(res.json())

    response = client.get("/api/contacts/upcoming-birthdays", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "birth_date" in data[0]
