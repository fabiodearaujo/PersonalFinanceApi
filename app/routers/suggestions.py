# necessary imports
from app import models, schemas
from app.database import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter()


# route to return all suggestions
@router.get("/")
async def get_all_suggestions(db: Session = Depends(get_db)):
    suggestions = db.query(models.Suggestion).all()
    return {"data": suggestions}, status.HTTP_200_OK


# route to add a suggestion
@router.post("/", status_code=201)
async def create_suggestion(
    suggestion: schemas.SuggestionCreate,
    db: Session = Depends(get_db),
):
    new_suggestion = models.Suggestion(**suggestion.dict())
    db.add(new_suggestion)
    db.commit()
    suggestion = (
        db.query(models.Suggestion)
        .order_by(models.Suggestion.suggestion_id.desc())
        .filter(
            models.Suggestion.category == suggestion.category,
        )
        .first()
    )
    return {"data": new_suggestion}, status.HTTP_201_CREATED


# route to return one suggestion
@router.get("/get_one/{suggestion_id}", status_code=200)
async def get_one_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    suggestion = (
        db.query(models.Suggestion)
        .filter(models.Suggestion.suggestion_id == suggestion_id)
        .first()
    )
    return {"data": suggestion}, status.HTTP_200_OK


# route to update a suggestion
@router.put("/update/{suggestion_id}", status_code=200)
async def update_suggestion(
    suggestion_id: int,
    suggestion: schemas.SuggestionUpdate,
    db: Session = Depends(get_db),
):
    suggestion_to_update = (
        db.query(models.Suggestion)
        .filter(models.Suggestion.suggestion_id == suggestion_id)
        .first()
    )
    suggestion_to_update.category = suggestion.category
    db.commit()
    return {"Message": "Suggestion updated succesfully."}, status.HTTP_200_OK


# route to delete a suggestion
@router.delete("/delete/{suggestion_id}", status_code=200)
async def delete_suggestion(
    suggestion_id: int,
    confirm: str,
    db: Session = Depends(get_db),
):
    suggestion_to_delete = (
        db.query(models.Suggestion)
        .filter(models.Suggestion.suggestion_id == suggestion_id)
        .first()
    )
    if confirm.lower() == "n":
        return {"error": "Deletion Canceled."}, status.HTTP_400_BAD_REQUEST
    db.delete(suggestion_to_delete)
    db.commit()
    return {"data": "Suggestion deleted"}, status.HTTP_200_OK
