# necessary imports
from app import models, oauth2, schemas
from app.database import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter()


# route to return all transactions from a user
@router.get("/", status_code=200)
def get_all_transactions(
    db: Session = Depends(get_db),
    user_auth: int = Depends(oauth2.get_current_user),
):
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.user_id == user_auth.user_id)
        .all()
    )
    # verify if it is the correct user
    if transactions[0].user_id != user_auth.user_id:
        return {"error": "Unauthorized Access."}, status.HTTP_401_UNAUTHORIZED
    return {"data": transactions}, status.HTTP_200_OK


# route to return one transaction
@router.get("/get_one", status_code=200)
async def get_one_transaction(
    transaction: schemas.TransactionGetOne,
    db: Session = Depends(get_db),
    user_auth: int = Depends(oauth2.get_current_user),
):
    transaction_to_get = (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_id == transaction.transaction_id)
        .first()
    )

    # verify if it is the correct user
    if transaction_to_get.user_id != user_auth.user_id:
        return {"error": "Unauthorized Access."}, status.HTTP_401_UNAUTHORIZED
    return {"data": transaction_to_get}, status.HTTP_200_OK


# route to add a transaction
@router.post("/create", status_code=201)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    user_auth: int = Depends(oauth2.get_current_user),
):
    existing_user = (
        db.query(models.User)
        .filter(models.User.user_id == transaction.user_id,)
        .first()
    )

    # verify if it is the correct user
    if transaction.user_id != int(user_auth.user_id):
        return {"error": "Unauthorized Access."}, status.HTTP_401_UNAUTHORIZED
    if existing_user is None:
        return {"error": "There is no user with that id"}, status.HTTP_404_NOT_FOUND
    new_transaction = models.Transaction(**transaction.dict())
    db.add(new_transaction)
    db.commit()
    
    return {"Message": "Transaction created successfully."}, status.HTTP_201_CREATED


# route to edit a transaction
@router.put("/update", status_code=200)
async def edit_transaction(
    transaction: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    user_auth: int = Depends(oauth2.get_current_user),
):
    transaction_to_edit = (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_id == transaction.transaction_id)
        .first()
    )

    # verify if it is the correct user
    if transaction_to_edit.user_id != user_auth.user_id:
        return {"error": "Unauthorized Access."}, status.HTTP_401_UNAUTHORIZED
    if transaction_to_edit.transaction_category == "transfer":
        return {
            "error": "You cannot edit a transfer transaction"
        }, status.HTTP_400_BAD_REQUEST
    transaction_to_edit.transaction_name = transaction.transaction_name
    transaction_to_edit.transaction_category = transaction.transaction_category
    transaction_to_edit.transaction_type = transaction.transaction_type
    transaction_to_edit.transaction_value = transaction.transaction_value
    transaction_to_edit.transaction_date = transaction.transaction_date
    db.commit()
    return {"data": "Transaction updated successfully."}, status.HTTP_200_OK


# route to delete a transaction
@router.delete("/delete", status_code=200)
async def delete_transaction(
    transaction: schemas.TransactionDelete,
    db: Session = Depends(get_db),
    user_auth: int = Depends(oauth2.get_current_user),
):
    existing_transaction = (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_id == transaction.transaction_id)
        .first()
    )

    # verify if it is the correct user
    if existing_transaction.user_id != user_auth.user_id:
        return {"error": "Unauthorized Access."}, status.HTTP_401_UNAUTHORIZED
    if existing_transaction.transaction_category == "transfer":
        return {
            "error": "You cannot delete a transfer transaction"
        }, status.HTTP_400_BAD_REQUEST
    if transaction.confirm != True:
        return {"error": "Deletion canceled."}, status.HTTP_400_BAD_REQUEST
    db.delete(existing_transaction)
    db.commit()
    return {"data": "Transaction deleted successfully"}, status.HTTP_200_OK


# route to move funds from one account to another
@router.post("/move_funds", status_code=201)
async def move_funds(
    move_funds: schemas.MoveFunds,
    db: Session = Depends(get_db),
    user_auth: int = Depends(oauth2.get_current_user),
):
    # verify if it is the correct user
    if move_funds.user_id != user_auth.user_id:
        return {"error": "Unauthorized Access."}, status.HTTP_401_UNAUTHORIZED

    # defining the direction of the transaction
    if move_funds.account_type == "main":
        account_debit = "savings"
        account_credit = "main"
    else:
        account_debit = "main"
        account_credit = "savings"

    # get the origin account balance
    check_account_credit = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == move_funds.user_id,
            models.Transaction.account_type == account_debit,
            models.Transaction.transaction_type == "credit",
        )
        .all()
    )
    # get the total credit amount of origin account
    check_account_credit_total = 0
    for transaction in check_account_credit:
        check_account_credit_total += transaction.transaction_value

    # get the origin account debits
    check_account_debit = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == move_funds.user_id,
            models.Transaction.account_type == account_debit,
            models.Transaction.transaction_type == "debit",
        )
        .all()
    )

    # get the total debit amount of origin account
    check_account_debit_total = 0
    for transaction in check_account_debit:
        check_account_debit_total += transaction.transaction_value

    check_account_balance = check_account_credit_total - check_account_debit_total

    # check if user has enough funds to move funds
    if check_account_balance < move_funds.transaction_value:
        return {
            "error": "Not enough funds to move. Transaction cancelled."
        }, status.HTTP_400_BAD_REQUEST

    # debit transaction
    debit_transaction = models.Transaction(
        user_id=move_funds.user_id,
        transaction_name="Transfer funds",
        transaction_category="transfer",
        transaction_type="debit",
        transaction_value=move_funds.transaction_value,
        transaction_date=move_funds.transaction_date,
        account_type=account_debit,
    )
    db.add(debit_transaction)
    db.commit()

    # credit transaction
    credit_transaction = models.Transaction(
        user_id=move_funds.user_id,
        transaction_name="Receive funds",
        transaction_category="transfer",
        transaction_type="credit",
        transaction_value=move_funds.transaction_value,
        transaction_date=move_funds.transaction_date,
        account_type=account_credit,
    )
    db.add(credit_transaction)
    db.commit()
    return {
        "Message": "Funds moved successfully",
    }, status.HTTP_201_CREATED
