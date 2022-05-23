from http import client
from decouple import config
from fastapi.testclient import TestClient
from app.main import app
from app import oauth2

client = TestClient(app)

# getting environment variables
user_pass2 = config("USER_PASS2")

# global variables to store the token and user information
user_test = {"email": "unit.test2@test.com", "password": user_pass2}
user_id = 0

# The suggestions routes are blocked to regular users.
# The following tests are to confirm none of the routes are accessible.


# test returning all suggestions
def test_get_suggestions():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]

    # get the suggestions
    response = client.get(
        "/suggestions", headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{
        "Message": "Only an Admin can execute this query."
    }, 401]


# test returning one suggestions
def test_get_one_suggestions():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]

    # get the suggestions
    response = client.get(
        "/suggestions/get_one",
        json={"suggestion_id": 1},
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{
        "Message": "Only an Admin can execute this query."
    }, 401]


# test create suggestion route
def test_create_suggestion():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]

    # get the suggestions
    response = client.post(
        "/suggestions/create",
        json={
            "category": "string",
            "description": "string"
        },
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{
        "Message": "Only an Admin can create new suggestions."
    }, 401]


# test updating one suggestion
def test_update_suggestions():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]

    # get the suggestions
    response = client.put(
        "/suggestions/update",
        json={
            "suggestion_id": 1,
            "category": "string",
            "description": "string"
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{
        "Message": "Only Admin can update suggestions."
    }, 401]


# test deleting a suggestion
def test_deleting_suggestions():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]

    # get the suggestions
    response = client.delete(
        "/suggestions/delete",
        json={
            "suggestion_id": 1,
            "confirm": True,
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{
        "Message": "Only an Admin can delete suggestions."
    }, 401]


# test delete user and its transactions in cascade
def test_delete_user_cascade():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]
    user_id = auth_user["user"]

    # user delete successfully
    response = client.delete(
        "/users/delete", json={
            "user_id": user_id,
            "password": user_test["password"],
            "confirm": "true"
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"Message": "User deleted successfully."}, 200]


# authenticate the user
def authenticate_user(user_email, user_password):

    context = {}

    # user authentication
    user_auth = client.post("/auth/", data={
        "username":user_email, "password":user_password
    })
    # separating the token from the response
    jwt_token = user_auth.json()["access_token"]

    # get the user id and token
    token_data = oauth2.verify_access_token(jwt_token, context)
    user_id = int(token_data.user_id)

    return {"token": jwt_token, "user": user_id}
