from fastapi import APIRouter, HTTPException
from app.models import CaseSearchRequest, CaseListResponse
from app.services import jagriti_scraper
from typing import Tuple

router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)

def get_location_ids(state_name: str, commission_name: str) -> Tuple[str, str]:
    """Helper function to convert text names to internal IDs."""
    states = jagriti_scraper.get_states()
    state_id = next((s['id'] for s in states if s['name'].lower() == state_name.lower()), None)
    if not state_id:
        raise HTTPException(status_code=404, detail=f"State '{state_name}' not found.")

    commissions = jagriti_scraper.get_commissions(state_id)
    commission_id = next((c['id'] for c in commissions if c['name'].lower() == commission_name.lower()), None)
    if not commission_id:
        raise HTTPException(status_code=404, detail=f"Commission '{commission_name}' not found in {state_name}.")
    
    return state_id, commission_id

SEARCH_TYPE_MAPPING = {
    "case-number": "1",
    "complainant": "2",
    "respondent": "3",
    "complainant-advocate": "4",
    "respondent-advocate": "5",
    "industry-type": "6",
    "judge": "7",
}

def create_search_endpoint(search_type: str):
    """A factory to dynamically create the endpoint functions to avoid repetition."""
    def endpoint(req: CaseSearchRequest) -> CaseListResponse:
        state_id, commission_id = get_location_ids(req.state, req.commission)
        search_by_value = SEARCH_TYPE_MAPPING[search_type]
        
        cases_data = jagriti_scraper.search_cases(
            state_id=state_id,
            commission_id=commission_id,
            search_by=search_by_value,
            search_value=req.search_value
        )
        return CaseListResponse(cases=cases_data)
    return endpoint

# Dynamically create all 7 required endpoints from the mapping
for search_name in SEARCH_TYPE_MAPPING.keys():
    router.post(f"/by-{search_name}", response_model=CaseListResponse)(
        create_search_endpoint(search_name)
    )