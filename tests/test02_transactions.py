from http import client
from fastapi.testclient import TestClient
from app.main import app
from app import oauth2

client = TestClient(app)

# global variables to store the token and user information
user_test = {"email": "test@test.com", "password": "test"}
user_id = 0


# test create a new transaction
def test_create_transactions():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]
    user_id = auth_user["user"]

    # create successful transaction
    response = client.post(
        "/transactions/create", json={
            "user_id": user_id,
            "transaction_name": "Initial balance",
            "transaction_category": "initial balance",
            "transaction_type": "credit",
            "transaction_value": 2525.25,
            "transaction_date": "2022-05-01",
            "account_type": "main"
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"Message": "Transaction created successfully."}, 201]

    response = client.post(
        "/transactions/create", json={
            "user_id": user_id,
            "transaction_name": "shop expenses",
            "transaction_category": "food",
            "transaction_type": "debit",
            "transaction_value": 50.12,
            "transaction_date": "2022-05-02",
            "account_type": "main"      
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"Message": "Transaction created successfully."}, 201]

    # creating a transaction with an invalid user id when using the API manually
    # this operation should not be possible to happen through the APP.
    response = client.post(
        "/transactions/create", json={
            "user_id": user_id+1,
            "transaction_name": "shop expenses",
            "transaction_category": "food",
            "transaction_type": "debit",
            "transaction_value": 50.12,
            "transaction_date": "2022-05-02",
            "account_type": "main"      
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{
        "error": "Not possible to create transaction to another user."
        }, 401]


# test return all transactions
def test_get_all_transactions():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]

    # return all transactions
    response = client.get(
        "/transactions/", headers={"Authorization": f"Bearer {jwt_token}"}
    )
    transaction_id = response.json()[0]["data"][0]["transaction_id"]
    assert response.status_code == 200
    return transaction_id

# test return one transaction
def test_get_one_transaction():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]
    user_id = auth_user["user"]

    transaction = test_get_all_transactions()

    # return one transactions
    response = client.get(
        "/transactions/get_one",
        json={"transaction_id": transaction},
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"data": {
            "transaction_id": transaction,
            "user_id": user_id,
            "transaction_name": "Initial balance",
            "transaction_category": "initial balance",
            "transaction_type": "credit",
            "transaction_value": 2525.25,
            "transaction_date": "2022-05-01",
            "account_type": "main"
            }}, 200]


# edit a transaction
def test_edit_transaction():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]

    transaction = test_get_all_transactions()
    
    # edit one transactions
    response = client.put(
        "/transactions/update",
        json={
            "transaction_id": transaction,
            "transaction_name": "salary",
            "transaction_category": "income",
            "transaction_type": "credit",
            "transaction_value": 2800,
            "transaction_date": "2022-04-15",
            "account_type": "main"
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"Message": "Transaction updated successfully."}, 200]


# move funds from one account to another
def test_move_funds():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]
    user_id = auth_user["user"]

    # move funds from one account to another
    response = client.post(
        "/transactions/move_funds",
        json={
            "user_id": user_id,
            "transaction_value": 500,
            "transaction_date": "2022-05-05",
            "account_type": "savings"
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"Message": "Funds moved successfully"}, 201]

    # move funds from one account to another
    response = client.post(
        "/transactions/move_funds",
        json={
            "user_id": user_id,
            "transaction_value": 100,
            "transaction_date": "2022-05-05",
            "account_type": "main"
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"Message": "Funds moved successfully"}, 201]

    # return error if value is highed than the account balance
    response = client.post(
        "/transactions/move_funds",
        json={
            "user_id": user_id,
            "transaction_value": 50000,
            "transaction_date": "2022-05-05",
            "account_type": "savings"
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{
        "error": "Not enough funds to move. Transaction cancelled."
    }, 400]


# delete a transaction
def test_delete_transaction():

    # authenticate the user
    auth_user = authenticate_user(user_test["email"], user_test["password"])
    jwt_token = auth_user["token"]

    transaction = test_get_all_transactions()

    # user cancel delete one transactions
    response = client.delete(
        "/transactions/delete",
        json={
            "transaction_id": transaction,
            "confirm": False
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"error": "Deletion canceled."}, 400]

    # user confirm delete one transactions
    response = client.delete(
        "/transactions/delete",
        json={
            "transaction_id": transaction,
            "confirm": True
        }, headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.json() == [{"Message": "Transaction deleted successfully"}, 200]


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
