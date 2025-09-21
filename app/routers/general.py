from fastapi import APIRouter, HTTPException
from app.services import jagriti_scraper
from app.models import StateListResponse, CommissionListResponse

router = APIRouter()

@router.get("/states", response_model=StateListResponse, tags=["General"])
def list_states():
    """Retrieves a list of all available states and their internal IDs."""
    try:
        states_data = jagriti_scraper.get_states()
        return {"states": states_data}
    except HTTPException as e:
        raise e

@router.get("/commissions/{state_id}", response_model=CommissionListResponse, tags=["General"])
def list_commissions(state_id: str):
    """Retrieves a list of all available commissions for a given state ID."""
    try:
        commissions_data = jagriti_scraper.get_commissions(state_id=state_id)
        return {"commissions": commissions_data}
    except HTTPException as e:
        raise e