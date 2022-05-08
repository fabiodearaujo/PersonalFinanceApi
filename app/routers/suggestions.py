# necessary imports
from app import models, oauth2, schemas
from app.database import get_db
from decouple import config
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter()

# set the environment variable for special access
TOKEN_SPECIAL = config("TOKEN_SPECIAL")


# route to return all suggestions
@router.get("/")
async def get_all_suggestions(
    user_auth: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):

    # verify if user has special access
    if not verify_user_access(user_auth.user_id, db):
        return {
            "Message": "Only an Admin can execute this query."
        }, status.HTTP_401_UNAUTHORIZED
    suggestions = await db.query(models.Suggestion).all()
    return await {"data": suggestions}, status.HTTP_200_OK


# route to add a suggestion
@router.post("/create", status_code=201)
async def create_suggestion(
    suggestion: schemas.SuggestionCreate,
    db: Session = Depends(get_db),
    user_auth: int = Depends(oauth2.get_current_user),
):

    # verify if user has special access
    if not verify_user_access(user_auth.user_id, db):
        return {
            "Message": "Only an Admin can create new suggestions."
        }, status.HTTP_401_UNAUTHORIZED
    new_suggestion = models.Suggestion(**suggestion.dict())
    db.add(new_suggestion)
    db.commit()
    return {
        "data": "The new suggestion was created successfully."
    }, status.HTTP_201_CREATED


# route to return one suggestion
@router.get("/get_one", status_code=200)
async def get_one_suggestion(
    suggestion: schemas.SuggestionGetOne,
    db: Session = Depends(get_db),
    user_auth: int = Depends(oauth2.get_current_user),
):

   # verify if user has special access
    if not verify_user_access(user_auth.user_id, db):
        return {
            "Message": "Only an Admin can execute this query."
        }, status.HTTP_401_UNAUTHORIZED
    suggestion = (
        db.query(models.Suggestion)
        .filter(models.Suggestion.suggestion_id == suggestion.suggestion_id)
        .first()
    )
    return {"data": suggestion}, status.HTTP_200_OK


# route to update a suggestion
@router.put("/update", status_code=200)
async def update_suggestion(
    suggestion_update: schemas.SuggestionUpdate,
    db: Session = Depends(get_db),
    user_auth: int = Depends(oauth2.get_current_user),
):

   # verify if user has special access
    if not verify_user_access(user_auth.user_id, db):
        return {
            "Message": "Only Admin can update suggestions."
        }, status.HTTP_401_UNAUTHORIZED

    # get the suggestion to update
    suggestion_to_update = (
        db.query(models.Suggestion)
        .filter(models.Suggestion.suggestion_id == suggestion_update.suggestion_id)
        .first()
    )
    suggestion_to_update.category = suggestion_update.category
    suggestion_to_update.description = suggestion_update.description
    db.commit()
    return {"Message": "Suggestion updated succesfully."}, status.HTTP_200_OK


# route to delete a suggestion
@router.delete("/delete", status_code=200)
async def delete_suggestion(
    suggestion_info: schemas.SuggestionDelete,
    db: Session = Depends(get_db),
    user_auth: int = Depends(oauth2.get_current_user),
):

   # verify if user has special access
    if not verify_user_access(user_auth.user_id, db):
        return {
            "Message": "Only an Admin can delete suggestions."
        }, status.HTTP_401_UNAUTHORIZED
    suggestion_to_delete = (
        db.query(models.Suggestion)
        .filter(models.Suggestion.suggestion_id == suggestion_info.suggestion_id)
        .first()
    )
    if suggestion_info.confirm != True:
        return {"error": "Deletion Canceled."}, status.HTTP_400_BAD_REQUEST
    db.delete(suggestion_to_delete)
    db.commit()
    return {"data": "Suggestion deleted"}, status.HTTP_200_OK


# Function to check if user has special access
def verify_user_access(user_id: int, db: Session = Depends(get_db)):
    user = (db.query(models.User).filter(models.User.user_id == user_id).first())
    if TOKEN_SPECIAL == user.email:
        return True
