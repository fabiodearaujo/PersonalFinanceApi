from http import client
from fastapi.testclient import TestClient
from app.main import app
from app import oauth2

client = TestClient(app)


# test create user route
def test_create_user():

    # create the user
    response = client.post("/users/create", json={
        "email": "unit.test@test.com", "password": "test"})
    assert response.json() == [{"Message": "User created successfully."}, 201]
    assert response.status_code == 201

    # return error if user already exists
    response = client.post("/users/create", json={
        "email": "unit.test@test.com", "password": "test"
    })
    assert response.json() == [{"error": "User already exists."}, 400]

    # return error if email is not valid
    response = client.post("/users/create", json={"email": "test", "password": "test"})
    assert response.json() == {
        "detail": [{
            "loc": [
                "body", "email"
            ], "msg": "value is not a valid email address", "type": "value_error.email"
        }]}


# global variables to store the token and user information
user_test = {"email": "test1@test.com", "password": "test"}
user_id = 0
context = {}


# test update user email route
def test_update_user_email():

    # create the user
    client.post("/users/create", json=user_test)

    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]
    user_id = auth_user["user"]

    # failing to update the email if new email already exists.
    response = client.put(
        "/users/email", json={
            "user_id": user_id,"email": "unit.test@test.com", "password": "test"            
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"error": "User already exists."}, 400]

    # update the email successfully
    response = client.put(
        "/users/email", json={
            "user_id": user_id,
            "email": "test10@test.com",
            "password": user_test["password"]            
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    user_test["email"] = "test10@test.com"
    assert response.json() == [{"Message": "User updated successfully."}, 200]


# test update user password route
def test_update_user_password():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]
    user_id = auth_user["user"]

    # user insert wrong password
    response = client.put(
        "/users/password", json={
            "user_id": user_id,"password": "tert", "new_password": "failed"            
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{'error': 'Credentials are incorrect.'}, 400]

    # user update password successfully
    response = client.put(
        "/users/password", json={
            "user_id": user_id,
            "password": user_test["password"],
            "new_password": "test10"
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    user_test["password"] = "test10"
    assert response.json() == [{"Message": "User password updated successfully."}, 200]


# test delete user route
def test_delete_user():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]
    user_id = auth_user["user"]

    # user do not confirm deletion
    response = client.delete(
        "/users/delete", json={
            "user_id": user_id,
            "password": user_test["password"],
            "confirm": "false"
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"error": "User not deleted. Not Confirmed."}, 400]

    # user delete successfully
    response = client.delete(
        "/users/delete", json={
            "user_id": user_id,
            "password": user_test["password"],
            "confirm": "true"
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"Message": "User deleted successfully."}, 200]


def authenticate_user(user_email, user_password):

    # user authentication
    user_auth = client.post("/auth/", data={
        "username":user_email, "password":user_password
    })
    # separating the token from the response
    jwt_token = user_auth.json()["access_token"]

    # get the user id from the token
    token_data = oauth2.verify_access_token(jwt_token, context)

    # store the user id in a global variable
    user_id = int(token_data.user_id)

    return {"token": jwt_token, "user": user_id}
