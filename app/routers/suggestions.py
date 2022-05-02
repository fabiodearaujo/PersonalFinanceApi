# necessary imports
from requests import Session
from ..database import get_db
from .. import models, schemas
from fastapi import APIRouter, Depends, status

router = APIRouter()

# route to return all suggestions
@router.get("/suggestions")
async def read_suggestions(db: Session = Depends(get_db)):
    suggestions = db.query(models.Suggestion).all()
    return {"data": suggestions}, status.HTTP_200_OK


# route to add a suggestion
@router.post("/suggestions", status_code=201)
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
