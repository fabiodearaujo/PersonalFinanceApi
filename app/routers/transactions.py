# necessary imports
from app import models, schemas
from app.database import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter()


# route to return all transactions from a user
@router.get("/{user_id}", status_code=200)
async def get_all_transactions(user_id: int, db: Session = Depends(get_db)):
    transactions = (
        db.query(models.Transaction).filter(models.Transaction.user_id == user_id).all()
    )
    return {"data": transactions}, status.HTTP_200_OK


# route to return one transaction
@router.get("/get_one/{transaction_id}", status_code=200)
async def get_one_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_id == transaction_id)
        .first()
    )
    return {"data": transaction}, status.HTTP_200_OK


# route to add a transaction
@router.post("/create", status_code=201)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(models.User)
        .filter(
            models.User.user_id == transaction.user_id,
        )
        .first()
    )
    if existing_user is None:
        return {"error": "There is no user with that id"}, status.HTTP_404_NOT_FOUND
    new_transaction = models.Transaction(**transaction.dict())
    db.add(new_transaction)
    db.commit()
    transaction = (
        db.query(models.Transaction)
        .order_by(models.Transaction.transaction_id.desc())
        .filter(
            models.Transaction.transaction_name == transaction.transaction_name
            and models.Transaction.user_id == transaction.user_id,
        )
        .first()
    )
    return {"data": transaction}, status.HTTP_201_CREATED


# route to edit a transaction
@router.put("/update/{transaction_id}", status_code=200)
async def edit_transaction(
    transaction_id: int,
    transaction: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
):
    transaction_to_edit = (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_id == transaction_id)
        .first()
    )
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
    return {"data": transaction_to_edit}, status.HTTP_200_OK


# route to delete a transaction
@router.delete("/delete/{transaction_id}", status_code=200)
async def delete_transaction(
    transaction_id: int,
    confirm: str,
    db: Session = Depends(get_db),
):
    existing_transaction = (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_id == transaction_id)
        .first()
    )
    if existing_transaction.transaction_category == "transfer":
        return {
            "error": "You cannot delete a transfer transaction"
        }, status.HTTP_400_BAD_REQUEST
    if confirm.lower() == "n":
        return {"error": "Deletion canceled."}, status.HTTP_400_BAD_REQUEST
    db.delete(existing_transaction)
    db.commit()
    return {"data": "Transaction deleted successfully"}, status.HTTP_200_OK


# route to move funds from one account to another
@router.post("/move_funds", status_code=201)
async def move_funds(
    user_id: int,
    transaction_value: float,
    transaction_date: str,
    account_type: str,
    db: Session = Depends(get_db),
):
    # defining the direction of the transaction
    if account_type == "main":
        account_debit = "savings"
        account_credit = "main"
    else:
        account_debit = "main"
        account_credit = "savings"

    # get the origin account balance
    check_account_credit = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == user_id,
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
            models.Transaction.user_id == user_id,
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
    if check_account_balance < transaction_value:
        return {
            "error": "Not enough funds to move. Transaction cancelled."
        }, status.HTTP_400_BAD_REQUEST

    # debit transaction
    debit_transaction = models.Transaction(
        user_id=user_id,
        transaction_name="Transfer funds",
        transaction_category="transfer",
        transaction_type="debit",
        transaction_value=transaction_value,
        transaction_date=transaction_date,
        account_type=account_debit,
    )
    db.add(debit_transaction)
    db.commit()

    # credit transaction
    credit_transaction = models.Transaction(
        user_id=user_id,
        transaction_name="Receive funds",
        transaction_category="transfer",
        transaction_type="credit",
        transaction_value=transaction_value,
        transaction_date=transaction_date,
        account_type=account_credit,
    )
    db.add(credit_transaction)
    db.commit()
    return {
        "Message": "Funds moved successfully",
    }, status.HTTP_201_CREATED
